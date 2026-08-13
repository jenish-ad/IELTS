import type { Metadata } from "next";
import type { ReactNode } from "react";
import Navbar from "../components/ui/Navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: "IELTS Practice",
  description: "Practice and track your IELTS preparation.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-svh bg-[#14264c] bg-[linear-gradient(rgb(7_18_45/30%),rgb(7_18_45/30%)),url('/image.png')] bg-cover bg-fixed bg-center bg-no-repeat font-sans text-white">
        <Navbar />
        {children}
      </body>
    </html>
  );
}
