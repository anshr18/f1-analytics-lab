"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navLinks = [
  { label: "Dashboard", href: "/" },
  { label: "Predictions", href: "/predictions" },
  { label: "Strategy", href: "/strategy" },
  { label: "Live Timing", href: "/live" },
  { label: "AI Assistant", href: "/assistant" },
];

export function TopNav() {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/" || pathname === "/dashboard";
    return pathname.startsWith(href);
  };

  return (
    <header className="hidden md:flex bg-[#0A0A0A] border-b border-[#2A2A2A] justify-between items-center w-full px-6 h-16 shrink-0 z-50">
      {/* Wordmark */}
      <div className="text-xl font-black text-[#E8002D] tracking-tighter italic select-none">
        F1 INTELLIGENCE HUB
      </div>

      {/* Nav links */}
      <nav className="flex h-full items-end gap-8">
        {navLinks.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`relative pb-4 h-full flex items-end text-xs font-bold uppercase tracking-widest transition-colors ${
              isActive(link.href)
                ? "text-white"
                : "text-[#666666] hover:text-[#E8002D]"
            }`}
          >
            {link.label}
            {isActive(link.href) && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#E8002D]" />
            )}
          </Link>
        ))}
      </nav>

      {/* Right icons */}
      <div className="flex items-center gap-4">
        <span className="material-symbols-outlined text-[#666666] hover:text-[#E8002D] cursor-pointer transition-colors text-[20px]">
          settings
        </span>
        <span className="material-symbols-outlined text-[#666666] hover:text-[#E8002D] cursor-pointer transition-colors text-[20px]">
          notifications
        </span>
        <div className="w-8 h-8 rounded-full bg-[#2a2a2a] border border-[#2A2A2A] flex items-center justify-center overflow-hidden ml-1">
          <span className="material-symbols-outlined text-[#666666] text-[18px]">person</span>
        </div>
      </div>
    </header>
  );
}
