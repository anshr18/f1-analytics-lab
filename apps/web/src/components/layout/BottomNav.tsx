"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { label: "Dashboard", href: "/", icon: "dashboard" },
  { label: "Predict", href: "/predictions", icon: "query_stats" },
  { label: "Strategy", href: "/strategy", icon: "timeline" },
  { label: "Live", href: "/live", icon: "timer" },
  { label: "AI", href: "/assistant", icon: "psychology" },
];

export function BottomNav() {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/" || pathname === "/dashboard";
    return pathname.startsWith(href);
  };

  return (
    <nav className="md:hidden fixed bottom-0 left-0 w-full flex justify-around items-center bg-[#141414] h-16 border-t border-[#2A2A2A] z-50">
      {navItems.map((item) => {
        const active = isActive(item.href);
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`flex flex-col items-center justify-center py-2 w-full h-full transition-colors active:scale-95 ${
              active ? "text-[#E8002D]" : "text-[#666666] hover:bg-[#1C1C1C]"
            }`}
          >
            <span
              className={`material-symbols-outlined mb-1 ${active ? "filled" : ""}`}
            >
              {item.icon}
            </span>
            <span className="text-[10px] font-bold uppercase tracking-tight">
              {item.label}
            </span>
          </Link>
        );
      })}
    </nav>
  );
}
