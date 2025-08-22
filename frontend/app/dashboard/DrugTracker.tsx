import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "@/components/ui/table";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import { Badge } from "@/components/ui/badge";
  import React, { useEffect, useState } from "react";
  
  interface Drug {
    drug: string;
    brandName: string;
    manufacturer: string;
    agency: string;
    therapeuticArea: string;
    status: "Completed" | "In Progress";
    lastUpdate: string;
    timeline: string;
  }
  
  const drugs: Drug[] = [
    {
      drug: "Ozempic",
      brandName: "Semaglutide",
      manufacturer: "Novo Nordisk",
      agency: "Health Canada",
      therapeuticArea: "Type 2 Diabetes",
      status: "Completed",
      lastUpdate: "Approved",
      timeline: "01-Jan-20"
    },
    {
      drug: "Keytruda",
      brandName: "Pembrolizumab",
      manufacturer: "Merck",
      agency: "INESSS",
      therapeuticArea: "Oncology",
      status: "In Progress",
      lastUpdate: "Clinical Trial Phase III",
      timeline: "15-Mar-23"
    },
    {
      drug: "Rinvoq",
      brandName: "Upadacitinib",
      manufacturer: "AbbVie",
      agency: "PCPA",
      therapeuticArea: "Rheumatoid Arthritis",
      status: "Completed",
      lastUpdate: "Negotiations Finalized",
      timeline: "10-Jul-22"
    }
  ];
  
  export const DrugTracker = () => {
    return (
      <Card className="h-full">
        <CardHeader>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Drug</TableHead>
                <TableHead>Brand Name</TableHead>
                <TableHead>Manufacturer</TableHead>
                <TableHead>Agency</TableHead>
                <TableHead>Therapeutic Area</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Latest Update</TableHead>
                <TableHead>Timeline</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {drugs.map((drug, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{drug.drug}</TableCell>
                  <TableCell>{drug.brandName}</TableCell>
                  <TableCell>{drug.manufacturer}</TableCell>
                  <TableCell>{drug.agency}</TableCell>
                  <TableCell>{drug.therapeuticArea}</TableCell>
                  <TableCell>
                    <Badge variant={drug.status === "Completed" ? "secondary" : "default"}>
                      {drug.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{drug.lastUpdate}</TableCell>
                  <TableCell>{drug.timeline}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    );
  };
  export default DrugTracker;