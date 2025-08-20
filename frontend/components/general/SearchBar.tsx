"use client";

import React from "react";
import { Search } from "lucide-react";

export const SearchBar = () => {
    return (
        <div className="flex items-center border border-var-(--foreground)-300 rounded-lg px-3 py-2 max-w-xl w-full bg-var-(--foreground)">
        <Search id="search-icon" color="var(--button-red)"/>
        <input className="px-3 flex-grow placeholder-[var(--foreground)] text-[var(--foreground)]"
        placeholder="Search drugs, therapeautic area, etc."/>
        </div>
    )
}
export default SearchBar;