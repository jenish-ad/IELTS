"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Home" },
  { href: "/practice/speaking", label: "Practice" },
  { href: "/progress", label: "Progress" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="absolute inset-x-0 top-0 z-10 bg-gradient-to-b from-[rgb(7_18_45/46%)] to-transparent">
      <nav
        className="mx-auto grid min-h-[82px] w-[min(1475px,calc(100%-64px))] grid-cols-[1fr_auto_1fr] items-center gap-[34px] max-[1000px]:grid-cols-[auto_1fr] max-[600px]:min-h-[70px] max-[600px]:w-[calc(100%-28px)] max-[600px]:gap-4"
        aria-label="Main navigation"
      >
        <Link
          className="relative w-max pb-[7px] text-[29px] font-light tracking-[-1px] max-[600px]:text-[21px]"
          href="/"
          aria-label="IELTSMate home"
        >
          <span className="font-extrabold">IELTS</span>
          <span>Mate</span>
          <span className="absolute right-0 bottom-0 h-[3px] w-[58px] -rotate-3 rounded-[50%] bg-[#ff5541]" aria-hidden="true" />
        </Link>

        <div className="flex items-center gap-9 max-[1000px]:hidden">
          {links.map((link) => {
            const isActive = link.href === "/" ? pathname === "/" : pathname.startsWith(link.href);

            return (
              <Link
                className={`relative pt-[30px] pb-[25px] text-base font-semibold transition-colors duration-150 ${
                  isActive
                    ? "text-white after:absolute after:right-[15%] after:bottom-[18px] after:left-[15%] after:h-[3px] after:rounded-full after:bg-[#ff5541]"
                    : "text-white/80 hover:text-white"
                }`}
                href={link.href}
                key={link.href}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </header>
  );
}
