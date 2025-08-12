import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "東京ウェルビーイング居住地マップ",
  description: "子育て世代のための東京都内居住地選びサポートツール",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <div className="min-h-screen bg-gray-50">
          <header className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                <h1 className="text-xl font-bold text-gray-900">
                  東京ウェルビーイング居住地マップ
                </h1>
                <nav className="flex space-x-8">
                  <a href="/" className="text-gray-700 hover:text-gray-900">
                    ホーム
                  </a>
                  <a href="/search" className="text-gray-700 hover:text-gray-900">
                    検索
                  </a>
                  <a href="/compare" className="text-gray-700 hover:text-gray-900">
                    比較
                  </a>
                  <a href="/simulation" className="text-gray-700 hover:text-gray-900">
                    シミュレーション
                  </a>
                </nav>
              </div>
            </div>
          </header>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
