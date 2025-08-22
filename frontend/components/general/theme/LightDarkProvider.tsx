"use client";

import { ThemeProvider } from "next-themes";

export function LightDarkProvider ( {children}: {children: React.ReactNode}){
        // return (
        // <ThemeProvider enableSystem={true} attribute="class">
        //     {children}
        // </ThemeProvider>
        // );
        return (
            <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
              {children}
            </ThemeProvider>
          );
    }