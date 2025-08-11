"use client";
import NewsCard from "./NewsCard";
import DrugTracker from "./DrugTracker";
import ProjectCard from "./ProjectCard";
import TherapeuticChart from "./TherapeuticChart";
import React, { useEffect, useState } from "react";

const Dashboard = () => {
  const newsItems = [
    {
      title: "News #1",
      description: "The latest news on the drug class or therapeutic area of interest."
    },
    {
      title: "News #2", 
      description: "The latest news on the drug class or therapeutic area of interest."
    },
    {
      title: "News #3",
      description: "The latest news on the drug class or therapeutic area of interest."
    }
  ];

  const projects = [
    {
      title: "Project #1",
      therapeuticArea: "Diabetes I",
      predictionType: "approval" as const,
      value: "8 months"
    },
    {
      title: "Project #2",
      therapeuticArea: "Head and neck cancer", 
      predictionType: "pricing" as const,
      value: "$2,000 - 6,000"
    }
  ];

  return (
    <div className="min-h-screen bg-background p-6 space-y-8">
      {/* Latest Market Intelligence */}
      <section>
        <h1 className="text-3xl font-bold mb-6">Latest Market Intelligence</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {newsItems.map((item, index) => (
            <NewsCard key={index} title={item.title} description={item.description} />
          ))}
        </div>
      </section>

      {/* External Drugs Tracker */}
      <section className="bg-accent/20 p-6 rounded-lg">
        <DrugTracker />
      </section>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Internal Portfolio Predictions */}
        <section>
          <h2 className="text-2xl font-bold mb-6">Internal Portfolio Predictions</h2>
          <div className="space-y-6">
            {projects.map((project, index) => (
              <ProjectCard
                key={index}
                title={project.title}
                therapeuticArea={project.therapeuticArea}
                predictionType={project.predictionType}
                value={project.value}
              />
            ))}
          </div>
        </section>

        {/* Therapeutic Area Analysis */}
        <section>
          <TherapeuticChart />
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
