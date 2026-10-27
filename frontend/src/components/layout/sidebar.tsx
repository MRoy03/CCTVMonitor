"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Video,
  Zap,
  ClipboardList,
  FileText,
  Bell,
  ThumbsUp,
  Settings,
} from "lucide-react";

import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, enabled: true },
  { href: "/sources", label: "Sources", icon: Video, enabled: true },
  { href: "/rules", label: "Rules", icon: Zap, enabled: true },
  { href: "/profiles", label: "Monitoring Profiles", icon: ClipboardList, enabled: false },
  { href: "/reports", label: "Reports", icon: FileText, enabled: true },
  { href: "/alerts", label: "Alerts", icon: Bell, enabled: false },
  { href: "/feedback", label: "Feedback", icon: ThumbsUp, enabled: false },
  { href: "/settings", label: "Settings", icon: Settings, enabled: false },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-60 shrink-0 border-r bg-background md:flex md:flex-col">
      <div className="px-4 py-5 text-lg font-semibold">CIP</div>
      <nav className="flex flex-1 flex-col gap-1 px-2">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = pathname.startsWith(item.href);
          const content = (
            <span
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                item.enabled
                  ? active
                    ? "bg-secondary text-secondary-foreground"
                    : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
                  : "cursor-not-allowed text-muted-foreground/40",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
              {!item.enabled && <span className="ml-auto text-[10px]">soon</span>}
            </span>
          );

          return item.enabled ? (
            <Link key={item.href} href={item.href}>
              {content}
            </Link>
          ) : (
            <div key={item.href}>{content}</div>
          );
        })}
      </nav>
    </aside>
  );
}
