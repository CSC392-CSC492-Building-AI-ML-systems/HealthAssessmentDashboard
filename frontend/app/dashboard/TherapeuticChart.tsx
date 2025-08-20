import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import React, { useEffect, useState, createContext } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from "recharts";

const data = [
  { year: "2020.0", Cardiovascular: 3, Immunology: 2, "Infectious Disease": 1, Neurology: 2, Oncology: 4, "Rare Disease": 3 },
  { year: "2020.5", Cardiovascular: 3.5, Immunology: 2.5, "Infectious Disease": 1.5, Neurology: 2.5, Oncology: 4.5, "Rare Disease": 3.5 },
  { year: "2021.0", Cardiovascular: 4, Immunology: 3, "Infectious Disease": 2, Neurology: 3, Oncology: 5, "Rare Disease": 4 },
  { year: "2021.5", Cardiovascular: 4.5, Immunology: 3.5, "Infectious Disease": 2.5, Neurology: 3.5, Oncology: 5.5, "Rare Disease": 4.5 },
  { year: "2022.0", Cardiovascular: 5, Immunology: 4, "Infectious Disease": 3, Neurology: 4, Oncology: 6, "Rare Disease": 5 },
  { year: "2022.5", Cardiovascular: 5.5, Immunology: 4.5, "Infectious Disease": 3.5, Neurology: 4.5, Oncology: 6.5, "Rare Disease": 5.5 },
  { year: "2023.0", Cardiovascular: 6, Immunology: 5, "Infectious Disease": 4, Neurology: 5, Oncology: 7, "Rare Disease": 6 },
  { year: "2023.5", Cardiovascular: 6.5, Immunology: 5.5, "Infectious Disease": 4.5, Neurology: 5.5, Oncology: 7.5, "Rare Disease": 6.5 },
  { year: "2024.0", Cardiovascular: 7, Immunology: 6, "Infectious Disease": 5, Neurology: 6, Oncology: 8, "Rare Disease": 7 },
];

export const TherapeuticChart = () => {
  return (
    <Card>
      <CardHeader>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={data}>
            <CartesianGrid stroke={"var(--foreground)"} strokeDasharray="3 3" />
            <XAxis stroke="var(--foreground)" tick={{fill:"var(--foreground)"}} dataKey="year" />
            <YAxis stroke="var(--foreground)" tick={{fill:"var(--foreground)"}} 
            label={{ style: {fill: "var(--foreground)"}, value: "Number of Approvals", angle: -90, position: "insideLeft" }} />
            <Legend wrapperStyle={{color: "var(--foreground)"}}/>
            <Area
              type="monotone"
              dataKey="Cardiovascular"
              stackId="1"
              stroke="var(--foreground)"
              fill="var(--foreground)"
              fillOpacity={0.8}
            />
            <Area
              type="monotone"
              dataKey="Immunology"
              stackId="1"
              stroke="var(--foreground)"
              fill="var(--foreground)"
              fillOpacity={0.8}
            />
            <Area
              type="monotone"
              dataKey="Infectious Disease"
              stackId="1"
              stroke="var(--foreground)"
              fill="var(--foreground)"
              fillOpacity={0.8}
            />
            <Area
              type="monotone"
              dataKey="Neurology"
              stackId="1"
              stroke="var(--foreground)"
              fill="var(--foreground)"
              fillOpacity={0.8}
            />
            <Area
              type="monotone"
              dataKey="Oncology"
              stackId="1"
              stroke="var(--foreground)"
              fill="var(--foreground)"
              fillOpacity={0.8}
            />
            <Area
              type="monotone"
              dataKey="Rare Disease"
              stackId="1"
              stroke="var(--foreground)"
              fill="var(--foreground)"
              fillOpacity={0.8}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
export default TherapeuticChart;