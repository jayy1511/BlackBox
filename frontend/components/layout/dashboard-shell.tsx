"use client";

import {
  Activity,
  Boxes,
  Database,
  History,
  KeyRound,
  ShieldCheck,
  Terminal,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

type DashboardShellProps = {
  children: ReactNode;
};

const navItems = [
  {
    label: "Debugger",
    href: "/",
    icon: Terminal,
  },
  {
    label: "Runs",
    href: "/runs",
    icon: History,
  },
];

export function DashboardShell({ children }: DashboardShellProps) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-[#05070d] text-slate-100">
      <div className="flex min-h-screen">
        <aside className="hidden w-[260px] shrink-0 border-r border-white/10 bg-[#070a12] lg:block">
          <div className="flex h-16 items-center border-b border-white/10 px-5">
            <Link href="/" className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-cyan-400/25 bg-cyan-400/10">
                <Boxes className="h-4 w-4 text-cyan-300" />
              </div>
              <div>
                <div className="text-sm font-semibold tracking-tight text-white">
                  Blackbox
                </div>
                <div className="mt-0.5 text-[11px] text-slate-500">
                  LLM privacy console
                </div>
              </div>
            </Link>
          </div>

          <div className="px-3 py-4">
            <div className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-600">
              Workspace
            </div>

            <nav className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={[
                      "flex items-center gap-2 rounded-lg px-2.5 py-2 text-sm transition-colors",
                      isActive
                        ? "bg-white text-black"
                        : "text-slate-400 hover:bg-white/5 hover:text-slate-100",
                    ].join(" ")}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="absolute bottom-0 hidden w-[260px] border-t border-white/10 p-4 lg:block">
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
              <div className="flex items-center gap-2 text-xs font-medium text-slate-200">
                <Activity className="h-3.5 w-3.5 text-emerald-400" />
                Runtime checks
              </div>

              <div className="mt-3 space-y-2 text-[11px] text-slate-500">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  Input scan
                </div>
                <div className="flex items-center gap-2">
                  <KeyRound className="h-3.5 w-3.5" />
                  Tokenization
                </div>
                <div className="flex items-center gap-2">
                  <Database className="h-3.5 w-3.5" />
                  PostgreSQL trace
                </div>
              </div>
            </div>
          </div>
        </aside>

        <main className="min-w-0 flex-1">
          <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-white/10 bg-[#05070d]/85 px-4 backdrop-blur-xl sm:px-6 lg:px-8">
            <div>
              <div className="text-sm font-medium text-slate-200">
                Debugger
              </div>
              <div className="mt-0.5 text-xs text-slate-500">
                Inspect, tokenize, execute, and audit LLM prompts.
              </div>
            </div>

            <div className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs text-emerald-300">
              API connected
            </div>
          </header>

          <div className="mx-auto w-full max-w-[1500px] px-4 py-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}