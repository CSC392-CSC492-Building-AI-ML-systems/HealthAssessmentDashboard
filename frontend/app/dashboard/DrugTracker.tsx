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
      drug: "XXX",
      brandName: "N/A",
      manufacturer: "N/A",
      agency: "PCPA",
      therapeuticArea: "Diabetes I",
      status: "Completed",
      lastUpdate: "End of feedback period",
      timeline: "19-Apr-22"
    },
    {
      drug: "XXX",
      brandName: "N/A",
      manufacturer: "N/A",
      agency: "CDA",
      therapeuticArea: "Head and neck cancer",
      status: "Completed",
      lastUpdate: "Final recommendation posted",
      timeline: "16-May-25"
    },
    {
      drug: "XXX",
      brandName: "N/A",
      manufacturer: "N/A",
      agency: "INESSS",
      therapeuticArea: "Orthopedic cancer",
      status: "In Progress",
      lastUpdate: "Final recommendation posted",
      timeline: "11-Aug-25"
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