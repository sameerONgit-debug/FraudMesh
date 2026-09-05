import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FraudMesh - Detect the Network. Verify the Signal. Preserve the Evidence.",
  description: "Cross-institution financial fraud intelligence platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
