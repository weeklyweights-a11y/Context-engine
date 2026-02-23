import { useState, useEffect } from "react";
import {
  uploadFeedbackCsv,
  confirmFeedbackMapping,
  importFeedbackCsv,
  createFeedbackManual,
} from "../../services/feedbackApi";
import { getWizardAll } from "../../services/productApi";
import { FEEDBACK_SOURCES } from "../../types/feedback";

type Tab = "csv" | "manual";

const inputClass =
  "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 focus:ring-2 focus:ring-blue-500";
const labelClass = "block text-sm text-gray-400 mb-1";

export default function FeedbackUpload() {
  const [tab, setTab] = useState<Tab>("csv");
  const [file, setFile] = useState<File | null>(null);
  const [uploadId, setUploadId] = useState<string | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [mapping, setMapping] = useState<Record<string, string | null>>({});
  const [totalRows, setTotalRows] = useState(0);
  const [defaultSource, setDefaultSource] = useState<string>("support_ticket");
  const [useTodayForDate, setUseTodayForDate] = useState(true);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<{
    imported: number;
    failed: number;
    detected?: { name: string; count: number; is_new: boolean }[];
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [productAreas, setProductAreas] = useState<string[]>([]);
  const [showMapping, setShowMapping] = useState(false);
  const [autoDetectAreas, setAutoDetectAreas] = useState(true);
  const [autoAnalyzeSentiment, setAutoAnalyzeSentiment] = useState(true);
  const [previewSample, setPreviewSample] = useState<Record<string, string>[]>([]);

  // Manual form state
  const [manualText, setManualText] = useState("");
  const [manualSource, setManualSource] = useState<string>("support_ticket");
  const [manualArea, setManualArea] = useState("");
  const [manualAreaOther, setManualAreaOther] = useState("");
  const [manualCustomerName, setManualCustomerName] = useState("");
  const [manualAuthorName, setManualAuthorName] = useState("");
  const [manualAuthorEmail, setManualAuthorEmail] = useState("");
  const [manualDate, setManualDate] = useState(() =>
    new Date().toISOString().slice(0, 10)
  );
  const [manualRating, setManualRating] = useState<number | undefined>();
  const [manualAdding, setManualAdding] = useState(false);
  const [addAnother, setAddAnother] = useState(false);

  useEffect(() => {
    getWizardAll().then((res) => {
      const areasData = res.data?.areas;
      const areas = Array.isArray(areasData?.areas)
        ? (areasData.areas.map((a: { name?: string }) => a.name).filter(Boolean) as string[])
        : [];
      setProductAreas(areas);
    });
  }, []);

  const processFile = async (f: File) => {
    if (!f?.name.toLowerCase().endsWith(".csv")) {
      setError("Please select a CSV file");
      return;
    }
    setError(null);
    setImportResult(null);
    setShowMapping(false);
    try {
      const init = await uploadFeedbackCsv(f);
      setFile(f);
      setUploadId(init.upload_id);
      setColumns(init.columns);
      const suggested = init.suggested_mapping || {};
      setMapping(suggested);
      setTotalRows(init.total_rows);
      setPreviewSample(init.preview_sample ?? []);
      if (!suggested.text) setShowMapping(true);

      if (suggested.text) {
        setImporting(true);
        try {
          await confirmFeedbackMapping(init.upload_id, {
            column_mapping: suggested,
            default_source: defaultSource,
            use_today_for_date: useTodayForDate,
            auto_detect_areas: autoDetectAreas,
            auto_analyze_sentiment: autoAnalyzeSentiment,
          });
          const result = await importFeedbackCsv(init.upload_id);
          setImportResult({
            imported: result.imported_rows,
            failed: result.failed_rows,
            detected: result.detected_areas,
          });
        } catch (err: unknown) {
          setError(err instanceof Error ? err.message : "Import failed");
        } finally {
          setImporting(false);
        }
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) processFile(f);
    e.target.value = "";
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) processFile(f);
  };

  const handleDragOver = (e: React.DragEvent) => e.preventDefault();

  const handleConfirmAndImport = async () => {
    if (!uploadId || !mapping.text) {
      setError("Text column is required");
      return;
    }
    setImporting(true);
    setError(null);
    try {
      await confirmFeedbackMapping(uploadId, {
        column_mapping: mapping,
        default_source: defaultSource,
        use_today_for_date: useTodayForDate,
        auto_detect_areas: autoDetectAreas,
        auto_analyze_sentiment: autoAnalyzeSentiment,
      });
      const result = await importFeedbackCsv(uploadId);
      setImportResult({
        imported: result.imported_rows,
        failed: result.failed_rows,
        detected: result.detected_areas,
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Import failed");
    } finally {
      setImporting(false);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualText.trim()) return;
    setManualAdding(true);
    setError(null);
    try {
      const areaValue = manualArea === "__other__" ? manualAreaOther.trim() : manualArea;
      await createFeedbackManual({
        text: manualText.trim(),
        source: manualSource || undefined,
        product_area: areaValue || undefined,
        customer_name: manualCustomerName.trim() || undefined,
        author_name: manualAuthorName.trim() || undefined,
        author_email: manualAuthorEmail.trim() || undefined,
        rating: manualRating,
        created_at: `${manualDate}T12:00:00.000Z`,
      });
      if (!addAnother) {
        setManualText("");
        setManualArea("");
        setManualAreaOther("");
        setManualCustomerName("");
        setManualAuthorName("");
        setManualAuthorEmail("");
        setManualDate(new Date().toISOString().slice(0, 10));
        setManualRating(undefined);
        setTab("csv");
      } else {
        setManualText("");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to add feedback");
    } finally {
      setManualAdding(false);
    }
  };

  const FEEDBACK_FIELDS = [
    { key: "text", label: "Feedback text *" },
    { key: "source", label: "Source" },
    { key: "product_area", label: "Product area" },
    { key: "customer_name", label: "Customer" },
    { key: "date", label: "Date" },
    { key: "sentiment", label: "Sentiment" },
    { key: "rating", label: "Rating" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => { setTab("csv"); setError(null); setImportResult(null); }}
          className={`px-4 py-2 rounded-lg ${tab === "csv" ? "bg-blue-500 text-white" : "bg-gray-700 text-gray-400"}`}
        >
          CSV Upload
        </button>
        <button
          type="button"
          onClick={() => { setTab("manual"); setError(null); }}
          className={`px-4 py-2 rounded-lg ${tab === "manual" ? "bg-blue-500 text-white" : "bg-gray-700 text-gray-400"}`}
        >
          Manual Entry
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      {tab === "csv" && (
        <div className="space-y-4">
          {!uploadId ? (
            <label
              htmlFor="feedback-csv-input"
              className="block border-2 border-dashed border-gray-600 rounded-lg p-12 text-center hover:border-blue-500 cursor-pointer transition-colors"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <input
                id="feedback-csv-input"
                type="file"
                accept=".csv"
                className="hidden"
                onChange={handleFileChange}
              />
              <p className="text-gray-400">Drop CSV file or click to browse</p>
            </label>
          ) : (
            <>
              <p className="text-sm text-gray-400">{totalRows} rows • {file?.name}</p>
              {!mapping.text && (
                <p className="text-yellow-400 text-sm">Could not auto-detect feedback text column. Please map columns below.</p>
              )}
              {importing && !importResult && (
                <p className="text-blue-400">Importing {totalRows} items…</p>
              )}
              {importResult ? (
                <button
                  type="button"
                  onClick={() => setShowMapping(!showMapping)}
                  className="text-sm text-blue-400 hover:text-blue-300"
                >
                  {showMapping ? "Hide" : "View"} column mapping used
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => setShowMapping(!showMapping)}
                  className="text-sm text-blue-400 hover:text-blue-300"
                >
                  {showMapping ? "Hide" : "Customize"} column mapping
                </button>
              )}
              {(showMapping || !mapping.text) && (
              <>
              <div className="space-y-2">
                <div>
                  <label className={labelClass}>Default source (if not in CSV)</label>
                  <select
                    value={defaultSource}
                    onChange={(e) => setDefaultSource(e.target.value)}
                    className={inputClass}
                  >
                    {FEEDBACK_SOURCES.map((s) => (
                      <option key={s.id} value={s.id}>{s.label}</option>
                    ))}
                  </select>
                </div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={useTodayForDate}
                    onChange={(e) => setUseTodayForDate(e.target.checked)}
                  />
                  <span className="text-gray-400">Use today&apos;s date when not in CSV</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={autoDetectAreas}
                    onChange={(e) => setAutoDetectAreas(e.target.checked)}
                  />
                  <span className="text-gray-400">Auto-detect product areas</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={autoAnalyzeSentiment}
                    onChange={(e) => setAutoAnalyzeSentiment(e.target.checked)}
                  />
                  <span className="text-gray-400">Auto-analyze sentiment</span>
                </label>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-400">
                      <th className="pb-2">Our field</th>
                      <th className="pb-2">CSV column</th>
                    </tr>
                  </thead>
                  <tbody>
                    {FEEDBACK_FIELDS.map(({ key, label }) => (
                      <tr key={key}>
                        <td className="py-1">{label}</td>
                        <td>
                          <select
                            value={mapping[key] ?? ""}
                            onChange={(e) => setMapping((m) => ({ ...m, [key]: e.target.value || null }))}
                            className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-gray-100"
                          >
                            <option value="">—</option>
                            {columns.map((c) => (
                              <option key={c} value={c}>{c}</option>
                            ))}
                          </select>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {previewSample.length > 0 && !importResult && (
                <div>
                  <p className="text-sm text-gray-400 mb-2">Preview (first {Math.min(5, previewSample.length)} rows)</p>
                  <div className="overflow-x-auto rounded border border-gray-700">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-left text-gray-400 bg-gray-800/50">
                          <th className="px-3 py-2">Text</th>
                          <th className="px-3 py-2">Source</th>
                          <th className="px-3 py-2">Customer</th>
                          <th className="px-3 py-2">Date</th>
                          <th className="px-3 py-2">Rating</th>
                        </tr>
                      </thead>
                      <tbody>
                        {previewSample.map((row, i) => (
                          <tr key={i} className="border-t border-gray-700">
                            <td className="px-3 py-2 text-gray-300 max-w-xs truncate" title={row.text}>{row.text ?? "—"}</td>
                            <td className="px-3 py-2 text-gray-400">{row.source ?? "—"}</td>
                            <td className="px-3 py-2 text-gray-400">{row.customer_name ?? "—"}</td>
                            <td className="px-3 py-2 text-gray-400">{row.date ?? row.created_at ?? "—"}</td>
                            <td className="px-3 py-2 text-gray-400">{row.rating ?? "—"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{totalRows} items to import</p>
                </div>
              )}
              </>
              )}
              {importResult ? (
                <div className="p-4 bg-green-900/20 border border-green-700 rounded-lg">
                  <p className="text-green-400 font-medium">Imported {importResult.imported} items</p>
                  {importResult.failed > 0 && (
                    <p className="text-yellow-400 text-sm">{importResult.failed} rows failed</p>
                  )}
                  {importResult.detected && importResult.detected.length > 0 && (
                    <p className="text-gray-400 text-sm mt-2">
                      Detected areas: {importResult.detected.map((a) => `${a.name} (${a.count})`).join(", ")}
                    </p>
                  )}
                </div>
              ) : (showMapping || !mapping.text) && (
                <button
                  type="button"
                  onClick={handleConfirmAndImport}
                  disabled={importing || !mapping.text}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
                >
                  {importing ? "Importing…" : `Import ${totalRows} items`}
                </button>
              )}
            </>
          )}
        </div>
      )}

      {tab === "manual" && (
        <form onSubmit={handleManualSubmit} className="space-y-4 max-w-lg">
          <div>
            <label className={labelClass}>Feedback text *</label>
            <textarea
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
              rows={4}
              className={inputClass}
              required
            />
          </div>
          <div>
            <label className={labelClass}>Source</label>
            <select
              value={manualSource}
              onChange={(e) => setManualSource(e.target.value)}
              className={inputClass}
            >
              {FEEDBACK_SOURCES.map((s) => (
                <option key={s.id} value={s.id}>{s.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>Product area</label>
            <select
              value={manualArea}
              onChange={(e) => setManualArea(e.target.value)}
              className={inputClass}
            >
              <option value="">—</option>
              {productAreas.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
              <option value="__other__">Other / New</option>
            </select>
            {manualArea === "__other__" && (
              <input
                type="text"
                placeholder="Enter area name"
                value={manualAreaOther}
                onChange={(e) => setManualAreaOther(e.target.value)}
                className={`${inputClass} mt-1`}
              />
            )}
          </div>
          <div>
            <label className={labelClass}>Customer name</label>
            <input
              type="text"
              value={manualCustomerName}
              onChange={(e) => setManualCustomerName(e.target.value)}
              placeholder="Company or customer name"
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Author name</label>
            <input
              type="text"
              value={manualAuthorName}
              onChange={(e) => setManualAuthorName(e.target.value)}
              placeholder="Person who gave feedback"
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Author email</label>
            <input
              type="email"
              value={manualAuthorEmail}
              onChange={(e) => setManualAuthorEmail(e.target.value)}
              placeholder="author@example.com"
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Date</label>
            <input
              type="date"
              value={manualDate}
              onChange={(e) => setManualDate(e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Rating (1-5)</label>
            <select
              value={manualRating ?? ""}
              onChange={(e) => setManualRating(e.target.value ? Number(e.target.value) : undefined)}
              className={inputClass}
            >
              <option value="">—</option>
              {[1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={addAnother}
              onChange={(e) => setAddAnother(e.target.checked)}
            />
            <span className="text-gray-400">Add another</span>
          </label>
          <button
            type="submit"
            disabled={manualAdding || !manualText.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {manualAdding ? "Adding…" : "Add Feedback"}
          </button>
        </form>
      )}
    </div>
  );
}
