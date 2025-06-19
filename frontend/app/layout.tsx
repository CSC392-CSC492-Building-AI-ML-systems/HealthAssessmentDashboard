import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Footer from "@/components/general/Footer";
import Header from "@/components/general/Header";
import FAQ from "@/components/landing/FAQ";
import { LightDarkProvider } from "@/components/general/theme/LightDarkProvider";
import { Inter, Outfit } from 'next/font/google';
import "./globals.css";

// const geistSans = Geist({
//   variable: "--font-geist-sans",
//   subsets: ["latin"],
// });

// const geistMono = Geist_Mono({
//   variable: "--font-geist-mono",
//   subsets: ["latin"],
// });

// Replacing original text with the fonts from Figma. I've left the original fonts commented out just in case.

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

const outfit = Outfit({
  subsets: ['latin'],
  weight: ['400', '600', '700'],
  variable: '--font-outfit',
});

export const metadata: Metadata = {
  title: "OurPATHS",
  description: "Insurance Data Collector AI Assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    // <html lang="en" >
    <html lang="en" className={`${inter.variable} ${outfit.variable}`}>
      <body
        // className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <div className="flex flex-col min-h-screen">
          {/* Header */}
          <LightDarkProvider>
            <Header />

            {/* Middle content */}
            <main className="flex-1 p-2">
              {children}
            </main>
            <FAQ/>

            {/* Footer */}
            <Footer />
          </LightDarkProvider>
        </div>
      </body>
    </html>
  );
}
