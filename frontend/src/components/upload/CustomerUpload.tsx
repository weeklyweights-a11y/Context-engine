import { useState } from "react";
import {
  uploadCustomersCsv,
  confirmCustomerMapping,
  importCustomersCsv,
  createCustomerManual,
} from "../../services/customerApi";

type Tab = "csv" | "manual";

const inputClass =
  "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 focus:ring-2 focus:ring-blue-500";
const labelClass = "block text-sm text-gray-400 mb-1";

const CUSTOMER_FIELDS = [
  { key: "company_name", label: "Company name *" },
  { key: "customer_id_external", label: "Customer ID" },
  { key: "segment", label: "Segment" },
  { key: "plan", label: "Plan" },
  { key: "mrr", label: "MRR" },
  { key: "arr", label: "ARR" },
  { key: "account_manager", label: "Account manager" },
  { key: "renewal_date", label: "Renewal date" },
  { key: "health_score", label: "Health score" },
  { key: "industry", label: "Industry" },
  { key: "employee_count", label: "Employee count" },
];

export default function CustomerUpload() {
  const [tab, setTab] = useState<Tab>("csv");
  const [file, setFile] = useState<File | null>(null);
  const [uploadId, setUploadId] = useState<string | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [mapping, setMapping] = useState<Record<string, string | null>>({});
  const [totalRows, setTotalRows] = useState(0);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<{ imported: number; failed: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showMapping, setShowMapping] = useState(false);
  const [previewSample, setPreviewSample] = useState<Record<string, string>[]>([]);

  // Manual form state
  const [manualCompany, setManualCompany] = useState("");
  const [manualSegment, setManualSegment] = useState("");
  const [manualPlan, setManualPlan] = useState("");
  const [manualMrr, setManualMrr] = useState("");
  const [manualArr, setManualArr] = useState("");
  const [manualManager, setManualManager] = useState("");
  const [manualRenewal, setManualRenewal] = useState("");
  const [manualHealth, setManualHealth] = useState("");
  const [manualAdding, setManualAdding] = useState(false);

  const processFile = async (f: File) => {
    if (!f?.name.toLowerCase().endsWith(".csv")) {
      setError("Please select a CSV file");
      return;
    }
    setError(null);
    setImportResult(null);
    setShowMapping(false);
    try {
      const init = await uploadCustomersCsv(f);
      setFile(f);
      setUploadId(init.upload_id);
      setColumns(init.columns);
      const suggested = init.suggested_mapping || {};
      setMapping(suggested);
      setTotalRows(init.total_rows);
      setPreviewSample(init.preview_sample ?? []);
      if (!suggested.company_name) setShowMapping(true);

      if (suggested.company_name) {
        setImporting(true);
        try {
          await confirmCustomerMapping(init.upload_id, { column_mapping: suggested });
          const result = await importCustomersCsv(init.upload_id);
          setImportResult({
            imported: result.imported_rows,
            failed: result.failed_rows,
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
    if (!uploadId || !mapping.company_name) {
      setError("Company name column is required");
      return;
    }
    setImporting(true);
    setError(null);
    try {
      await confirmCustomerMapping(uploadId, { column_mapping: mapping });
      const result = await importCustomersCsv(uploadId);
      setImportResult({
        imported: result.imported_rows,
        failed: result.failed_rows,
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Import failed");
    } finally {
      setImporting(false);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualCompany.trim()) return;
    setManualAdding(true);
    setError(null);
    try {
      await createCustomerManual({
        company_name: manualCompany.trim(),
        segment: manualSegment.trim() || undefined,
        plan: manualPlan.trim() || undefined,
        mrr: manualMrr ? Number(manualMrr) : undefined,
        arr: manualArr ? Number(manualArr) : undefined,
        account_manager: manualManager.trim() || undefined,
        renewal_date: manualRenewal.trim() || undefined,
        health_score: manualHealth ? Number(manualHealth) : undefined,
      });
      setManualCompany("");
      setManualSegment("");
      setManualPlan("");
      setManualMrr("");
      setManualArr("");
      setManualManager("");
      setManualRenewal("");
      setManualHealth("");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to add customer");
    } finally {
      setManualAdding(false);
    }
  };

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
              htmlFor="customer-csv-input"
              className="block border-2 border-dashed border-gray-600 rounded-lg p-12 text-center hover:border-blue-500 cursor-pointer transition-colors"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <input
                id="customer-csv-input"
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
              {!mapping.company_name && (
                <p className="text-yellow-400 text-sm">Could not auto-detect company name column. Please map columns below.</p>
              )}
              {importing && !importResult && (
                <p className="text-blue-400">Importing {totalRows} customers…</p>
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
              {(showMapping || !mapping.company_name) && (
              <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-400">
                      <th className="pb-2">Our field</th>
                      <th className="pb-2">CSV column</th>
                    </tr>
                  </thead>
                  <tbody>
                    {CUSTOMER_FIELDS.map(({ key, label }) => (
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
                <div className="mt-4">
                  <p className="text-sm text-gray-400 mb-2">Preview (first {Math.min(5, previewSample.length)} rows)</p>
                  <div className="overflow-x-auto rounded border border-gray-700">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-left text-gray-400 bg-gray-800/50">
                          <th className="px-3 py-2">Company</th>
                          <th className="px-3 py-2">Segment</th>
                          <th className="px-3 py-2">MRR</th>
                          <th className="px-3 py-2">Health</th>
                          <th className="px-3 py-2">Renewal</th>
                        </tr>
                      </thead>
                      <tbody>
                        {previewSample.map((row, i) => (
                          <tr key={i} className="border-t border-gray-700">
                            <td className="px-3 py-2 text-gray-300">{row.company_name ?? "—"}</td>
                            <td className="px-3 py-2 text-gray-400">{row.segment ?? "—"}</td>
                            <td className="px-3 py-2 text-gray-400">{row.mrr ?? "—"}</td>
                            <td className="px-3 py-2 text-gray-400">{row.health_score ?? "—"}</td>
                            <td className="px-3 py-2 text-gray-400">{row.renewal_date ?? "—"}</td>
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
                  <p className="text-green-400 font-medium">Imported {importResult.imported} customers</p>
                  {importResult.failed > 0 && (
                    <p className="text-yellow-400 text-sm">{importResult.failed} rows failed</p>
                  )}
                </div>
              ) : (showMapping || !mapping.company_name) && (
                <button
                  type="button"
                  onClick={handleConfirmAndImport}
                  disabled={importing || !mapping.company_name}
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
            <label className={labelClass}>Company name *</label>
            <input
              type="text"
              value={manualCompany}
              onChange={(e) => setManualCompany(e.target.value)}
              className={inputClass}
              required
            />
          </div>
          <div>
            <label className={labelClass}>Segment</label>
            <input
              type="text"
              value={manualSegment}
              onChange={(e) => setManualSegment(e.target.value)}
              placeholder="e.g. Enterprise"
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Plan</label>
            <input
              type="text"
              value={manualPlan}
              onChange={(e) => setManualPlan(e.target.value)}
              className={inputClass}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>MRR</label>
              <input
                type="number"
                value={manualMrr}
                onChange={(e) => setManualMrr(e.target.value)}
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>ARR</label>
              <input
                type="number"
                value={manualArr}
                onChange={(e) => setManualArr(e.target.value)}
                className={inputClass}
              />
            </div>
          </div>
          <div>
            <label className={labelClass}>Account manager</label>
            <input
              type="text"
              value={manualManager}
              onChange={(e) => setManualManager(e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Renewal date</label>
            <input
              type="text"
              value={manualRenewal}
              onChange={(e) => setManualRenewal(e.target.value)}
              placeholder="YYYY-MM-DD"
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Health score (0-100)</label>
            <input
              type="number"
              min={0}
              max={100}
              value={manualHealth}
              onChange={(e) => setManualHealth(e.target.value)}
              className={inputClass}
            />
          </div>
          <button
            type="submit"
            disabled={manualAdding || !manualCompany.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {manualAdding ? "Adding…" : "Add Customer"}
          </button>
        </form>
      )}
    </div>
  );
}
