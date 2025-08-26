"use client";
import NewsCard from "./NewsCard";
import DrugTracker from "./DrugTracker";
import ProjectCard from "./ProjectCard";
import TherapeuticChart from "./TherapeuticChart";
import DrugButton from "@/components/general/DrugButton";
import React, { useEffect, useState } from "react";
import { Pill, Syringe } from "lucide-react";

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
      title: "Title #1",
      projectNumber: "project #1",
      therapeuticArea: "Diabetes I",
      predictionType: "Approval" as const,
      value: "8 months",
      status: "In Progress" as const,
      dose: "Injection" as const,
    },
    {
      title: "Title #2",
      projectNumber: "project #2",
      therapeuticArea: "Orthopedic Cancer", 
      predictionType: "Approval" as const,
      value: "3 months",
      status: "Accepted" as const,
      dose: "Pill" as const,
    }
  ];

  return (
    <div className="min-h-screen bg-background p-6 space-y-8">
      {/* Latest Market Intelligence */}
      <section>
        <h1 className="text-3xl font-bold text-[var(--foreground)] mb-6">Latest Market Intelligence</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {newsItems.map((item, index) => (
            <NewsCard key={index} title={item.title} description={item.description} />
          ))}
        </div>
      </section>

      {/* External Drugs Tracker */}
      <section className="w-full">
      <h2 className="text-2xl font-bold text-[var(--foreground)] mb-6">External Drug Tracker</h2>
        <DrugTracker />
      </section>

      {/* Bottom Section */}
        {/* Internal Portfolio Predictions */}
        <section>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <h2 className="text-2xl font-bold text-[var(--foreground)] mb-6">Internal Portfolio Predictions</h2>
        <div className="flex justify-end mb-6"> <DrugButton /> </div>
        </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {projects.map((project, index) => (
              <ProjectCard
                key={index}
                title={project.title}
                projectNumber={project.projectNumber}
                therapeuticArea={project.therapeuticArea}
                predictionType={project.predictionType}
                value={project.value}
                status={project.status}
                dose={project.dose}
              />
            ))}
          </div>
        </section>

      {/* Therapeutic Area Analysis */}
      <section>
        <h2 className="text-2xl font-bold text-[var(--foreground)] mb-6">Therapeutic Area Analysis</h2>
          <TherapeuticChart />
        </section>
    </div>
  );
};

export default Dashboard;
