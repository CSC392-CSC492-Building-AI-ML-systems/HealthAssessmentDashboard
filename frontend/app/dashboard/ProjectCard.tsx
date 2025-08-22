import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import React, { useEffect, useState } from "react";

interface ProjectCardProps {
  title: string;
  therapeuticArea: string;
  predictionType: "approval" | "pricing";
  value: string;
}

export const ProjectCard = ({ title, therapeuticArea, predictionType, value }: ProjectCardProps) => {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="font-medium text-sm text-(var(--foreground))">Therapeutic Area:</h4>
          <p className="text-sm">{therapeuticArea}</p>
        </div>
        <div>
          <h4 className="font-medium text-sm text-(var(--foreground))">
            {predictionType === "approval" ? "Predicted Approval Time:" : "Predicted Pricing:"}
          </h4>
          <p className="text-sm font-semibold text-(var(--foreground))">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
};
export default ProjectCard;