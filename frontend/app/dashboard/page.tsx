"use client";
import NewsCard from "./NewsCard";
import DrugTracker from "./DrugTracker";
import ProjectCard from "./ProjectCard";
import TherapeuticChart from "./TherapeuticChart";
import DrugButton from "@/components/general/DrugButton";
import React, { useEffect, useState } from "react";
import { Pill, Syringe } from "lucide-react";
import AddDrugModal from "@/components/general/AddDrugModal";
import { NewDrugPayload } from "@/lib/api";
// import { drugApi } from "@/lib/api/drug";


const Dashboard = () => {
  // Modal stuff
  const [showAdd, setShowAdd] = useState(false);

  async function handleAddDrug(data: NewDrugPayload) {
    console.log("New internal drug:", data);

    // const response = await drugApi.addDrug(data);
    // console.log(response.data)
  }
  const newsItems = [
    {
      title: "Sanofi Raises Annual Sales Forecast Amid Strong Dupixent Demand",
      description: "Sanofi has increased its annual sales growth forecast to a high single-digit percentage, driven by robust global demand for its anti-inflammatory drug Dupixent. The company also reaffirmed its low double-digit earnings growth projection for the year.",
      imageUrl: "/news1.jpg",
      linkUrl: "https://www.reuters.com/business/healthcare-pharmaceuticals/sanofi-raises-annual-sales-growth-expectations-strong-dupixent-demand-2025-07-31/"
    },
    {
      title: "Pfizer's Combination Therapy with Keytruda Shows Promise in Bladder Cancer Trial",
      description: "Pfizer's cancer drug Padcev, combined with Merck's Keytruda, significantly improved survival rates in patients with muscle-invasive bladder cancer, according to interim results from a late-stage trial.",
      imageUrl: "/news2.jpg",
      linkUrl: "https://www.reuters.com/business/healthcare-pharmaceuticals/pfizers-combination-therapy-improves-survival-bladder-cancer-trial-2025-08-12/"
    },
    {
      title: "AbbVie's Rinvoq Receives FDA Approval for Giant Cell Arteritis Treatment",
      description: "The FDA has approved AbbVie's Rinvoq (upadacitinib) for the treatment of adults with giant cell arteritis, marking its ninth approved indication across various therapeutic areas.",
      imageUrl: "/news3.jpg",
      linkUrl: "https://news.abbvie.com/2025-04-29-RINVOQ-R-upadacitinib-Receives-U-S-FDA-Approval-for-Giant-Cell-Arteritis-GCA"
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
            <NewsCard
              key={index}
              title={item.title}
              description={item.description}
              imageUrl={item.imageUrl}
              linkUrl={item.linkUrl}
            />
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

          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-2xl font-bold text-[var(--foreground)]">
              Internal Portfolio Predictions
            </h2>
            <button
              onClick={() => setShowAdd(true)}   // toggles modal open
              className="bg-[var(--button-red)] text-[var(--light-color)] px-3.5 py-2 rounded-full
                        transition-transform duration-300 hover:scale-105 hover:opacity-90 hover:shadow-xl"
            >
              +
            </button>
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
        <AddDrugModal
        open={showAdd}
        onClose={() => setShowAdd(false)}
        onSubmit={handleAddDrug}/>

      {/* Therapeutic Area Analysis */}
      <section>
        <h2 className="text-2xl font-bold text-[var(--foreground)] mb-6">Therapeutic Area Analysis</h2>
          <TherapeuticChart />
        </section>
    </div>
  );
};

export default Dashboard;
