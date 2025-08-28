import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import React, { useEffect, useState } from "react";

interface NewsCardProps {
  title: string;
  description: string;
  imageUrl: string;
  linkUrl: string;
}

export const NewsCard = ({ title, description, imageUrl, linkUrl }: NewsCardProps) => {
  return (
    <a href={linkUrl} target="_blank" rel="noopener noreferrer" className="block h-full">
      <Card className="h-full flex flex-col">
        <div className="relative h-40 w-full rounded-t-lg overflow-hidden">
          <img src={imageUrl} alt={title} className="w-full h-full object-cover" />
        </div>
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-(var(--foreground))">{title}</CardTitle>
        </CardHeader>
        <CardContent className="flex-grow">
          <p className="text-sm text-(var(--foreground))">{description}</p>
        </CardContent>
      </Card>
    </a>
  );
};
export default NewsCard;