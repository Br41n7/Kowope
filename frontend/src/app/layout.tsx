import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { NavBar } from "@/components/NavBar";

export const metadata: Metadata = {
  title: "TradeAfric",
  description: "Digital Trade Infrastructure Platform — trade desk",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col bg-parchment text-ink">
        <AuthProvider>
          <NavBar />
          <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-8">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
