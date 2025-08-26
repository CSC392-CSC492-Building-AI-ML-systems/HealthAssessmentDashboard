import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import React, { useEffect, useState } from "react";
import CircleIcon from '@mui/icons-material/Circle';
import { Pill, Syringe } from "lucide-react";

interface ProjectCardProps {
  title: string;
  projectNumber: string,
  therapeuticArea: string;
  predictionType: "Approval" | "pricing";
  value: string;
  status: "In Progress" | "Submitted" | "Accepted";
  dose: "Pill" | "Injection";
}

export const ProjectCard = ({ title, projectNumber, therapeuticArea, predictionType, value, status, dose }: ProjectCardProps) => {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">{title}</CardTitle>
        <CardTitle className="text-base opacity-70">{projectNumber}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="font-semibold text-sm text-[var(--foreground)]">Therapeutic Area:</h4>
          <p className="text-sm text-[var(--foreground)">{therapeuticArea}</p>
        </div>
        <div>
          <h4 className="font-semibold text-sm text-[var(--foreground)]">
            {predictionType === "Approval" ? "Predicted Approval Time:" : "Predicted Pricing:"}
          </h4>
          <p className="text-sm text-[var(--foreground)]">{value}</p>
        </div>
        <div>
          <h4 className="font-semibold text-sm text-[var(--foreground)]">
            Status:
          </h4>
          <p className="text-sm text-[var(--foreground)]">
          {status === "In Progress" ? <CircleIcon sx={{ color:'#E3D026', fontSize: 16 }}/>
          : status === "Accepted" ? <CircleIcon sx={{ color: "green", fontSize: 16 }}/> 
          : <CircleIcon sx={{ color: "red", fontSize: 16 }}/> }
            {status}</p>
            <div className="flex justify-end">
          { dose === "Injection" ? <Syringe size={45} />
          : <Pill size={45}/> }
        </div>
        </div>
      </CardContent>
    </Card>
  );
};
export default ProjectCard;