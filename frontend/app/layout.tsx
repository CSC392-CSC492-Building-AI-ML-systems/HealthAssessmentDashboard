import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Footer from "@/components/general/footer/FooterWithMode";
import Header from "@/components/general/header/HeaderWithMode";
import { cookies } from "next/headers";
import { LightDarkProvider } from "@/components/general/theme/LightDarkProvider";
import { ToastProvider } from "@/components/general/ToastProvider";
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
  description: "The Observational, Usable & Real-time Predictive Analytics Toolkit for Healthcare Strategy (OurPATHS)",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const themeCookie = cookieStore.get("theme");
  const theme = themeCookie ? themeCookie.value : "dark";
  return (
    // <html lang="en" >
    <html lang="en" className={theme} style={{ colorScheme: theme }}>
      <body
      // className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <div className="flex flex-col min-h-screen">
          {/* Header */}
          <LightDarkProvider>
            <ToastProvider position="top-center" maxToasts={3}>
              <Header />

              {/* Middle content */}
              <main className="flex-1">
                {children}
              </main>

              {/* Footer */}
              <Footer />
            </ToastProvider>
          </LightDarkProvider>
        </div>
      </body>
    </html>
  );
}
