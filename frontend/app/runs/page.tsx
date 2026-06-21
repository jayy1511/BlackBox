"use client";

import { useQuery } from "@tanstack/react-query";
import { Clock3, Database, ShieldAlert } from "lucide-react";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { listRuns } from "@/features/runs/api";

export default function RunsPage() {
  const runsQuery = useQuery({
    queryKey: ["runs"],
    queryFn: listRuns,
  });

  return (
    <DashboardShell>
      <div className="space-y-4">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-white">
              Runs
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Persisted privacy traces from Neon PostgreSQL.
            </p>
          </div>

          <Badge
            variant="outline"
            className="w-fit border-cyan-400/20 bg-cyan-400/10 text-cyan-300"
          >
            {runsQuery.data?.total ?? 0} total runs
          </Badge>
        </div>

        <div className="console-panel overflow-hidden">
          <div className="grid grid-cols-[1.2fr_0.8fr_0.8fr_0.8fr_0.8fr] border-b border-white/10 px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-600">
            <div>Run</div>
            <div>Status</div>
            <div>Risk</div>
            <div>Entities</div>
            <div>Model</div>
          </div>

          {runsQuery.isLoading ? (
            <div className="p-6 text-sm text-slate-500">Loading runs...</div>
          ) : runsQuery.data?.items.length === 0 ? (
            <div className="p-6 text-sm text-slate-500">No runs found.</div>
          ) : (
            <div className="divide-y divide-white/10">
              {runsQuery.data?.items.map((run) => (
                <div
                  key={run.run_id}
                  className="grid grid-cols-[1.2fr_0.8fr_0.8fr_0.8fr_0.8fr] px-4 py-4 text-sm hover:bg-white/[0.025]"
                >
                  <div>
                    <div className="font-mono text-xs text-slate-300">
                      {run.run_id.slice(0, 8)}...{run.run_id.slice(-6)}
                    </div>
                    <div className="mt-1 flex items-center gap-1.5 text-xs text-slate-600">
                      <Clock3 className="h-3 w-3" />
                      {new Date(run.created_at).toLocaleString()}
                    </div>
                  </div>

                  <div>
                    <Badge
                      variant="outline"
                      className="border-emerald-400/20 bg-emerald-400/10 text-emerald-300"
                    >
                      {run.status}
                    </Badge>
                  </div>

                  <div>
                    <div className="flex items-center gap-1.5 text-xs text-red-300">
                      <ShieldAlert className="h-3.5 w-3.5" />
                      {run.risk_level}
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center gap-1.5 text-xs text-slate-300">
                      <Database className="h-3.5 w-3.5 text-cyan-300" />
                      {run.entities_count}
                    </div>
                  </div>

                  <div className="font-mono text-xs text-slate-500">
                    {run.model_name}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {runsQuery.error ? (
          <Card className="border-red-400/20 bg-red-400/10">
            <CardContent className="p-4 text-sm text-red-200">
              {runsQuery.error instanceof Error
                ? runsQuery.error.message
                : "Failed to load runs"}
            </CardContent>
          </Card>
        ) : null}
      </div>
    </DashboardShell>
  );
}