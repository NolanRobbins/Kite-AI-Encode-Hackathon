"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/cn";
import { NegotiatorGridLogo } from "./logo";
import {
  LayoutDashboard,
  ArrowLeftRight,
  Handshake,
  Bot,
  Radio,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/negotiations/neg-047", label: "Negotiations", icon: ArrowLeftRight },
  { href: "/#deals", label: "Deals", icon: Handshake },
  { href: "/#agents", label: "Agents", icon: Bot },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-[220px] bg-[#0f1117] border-r border-[var(--color-border)] flex flex-col z-50">
      {/* Logo */}
      <div className="px-5 py-5 flex items-center gap-3 border-b border-[var(--color-border)]">
        <NegotiatorGridLogo size={28} />
        <div>
          <div className="text-sm font-semibold text-[var(--color-text)] leading-tight tracking-tight">
            NegotiatorGrid
          </div>
          <div className="text-[10px] font-mono text-[var(--color-text-faint)] leading-tight">
            Kite AI Protocol
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href.replace("/#", "/"));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                isActive
                  ? "bg-[var(--color-cyan-glow)] text-[var(--color-cyan)] font-medium"
                  : "text-[var(--color-text-muted)] hover:text-[var(--color-text)] hover:bg-[var(--color-card)]"
              )}
            >
              <Icon size={16} strokeWidth={1.8} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Status indicator */}
      <div className="px-4 py-4 border-t border-[var(--color-border)]">
        <div className="flex items-center gap-2 text-xs text-[var(--color-text-faint)]">
          <Radio size={12} className="text-[var(--color-deal)]" />
          <span className="text-[var(--color-deal)]">API Connected</span>
        </div>
        <div className="text-[10px] font-mono text-[var(--color-text-faint)] mt-1">
          kite-testnet v0.4.2
        </div>
      </div>
    </aside>
  );
}
