import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import React, { useEffect, useState } from "react";

interface NewsCardProps {
  title: string;
  description: string;
}

export const NewsCard = ({ title, description }: NewsCardProps) => {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-(var(--foreground))">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-(var(--foreground))">{description}</p>
      </CardContent>
    </Card>
  );
};
export default NewsCard;