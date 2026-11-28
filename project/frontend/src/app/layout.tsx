import type { Metadata } from "next";
import Link from "next/link";
import "@fontsource/dm-sans/latin-400.css";
import "@fontsource/dm-sans/latin-600.css";
import "@fontsource/instrument-serif/latin-400.css";
import "./styles.css";

export const metadata: Metadata = { title: "EstateFlow" };

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          <Link href="/">EstateFlow</Link>
        </header>
        <main className="mx-auto w-full max-w-5xl px-6 py-14 sm:py-20">{children}</main>
      </body>
    </html>
  );
}
