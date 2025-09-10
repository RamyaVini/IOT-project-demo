"use client";

import React from "react";
import { useEffect, useState } from "react";

type Event = {
  device_id: string;
  timestamp: string;
  ac_power: number;
  temperature_module: number;
  status: {
    operational: boolean;
  };
};

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [dateFilter, setDateFilter] = useState("");

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10; // records per page

  useEffect(() => {
    async function fetchEvents() {
      try {
        const res = await fetch("/api/events");
        const data = await res.json();
        setEvents(data);
      } catch (err) {
        console.error("Error fetching events", err);
      } finally {
        setLoading(false);
      }
    }
    fetchEvents();
  }, []);

  const filteredEvents = events.filter((e) => {
    const matchesDevice =
      !search || e.device_id.toLowerCase().includes(search.toLowerCase());
    const matchesDate = !dateFilter || e.timestamp.startsWith(dateFilter);
    return matchesDevice && matchesDate;
  });

  // Pagination logic
  const totalPages = Math.ceil(filteredEvents.length / pageSize);
  const paginatedEvents = filteredEvents.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">PV Device Events</h1>

      {/* Filters */}
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          placeholder="Search by device_id"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setCurrentPage(1); // reset to page 1
          }}
          className="border rounded px-2 py-1"
        />
        <input
          type="date"
          value={dateFilter}
          onChange={(e) => {
            setDateFilter(e.target.value);
            setCurrentPage(1); // reset to page 1
          }}
          className="border rounded px-2 py-1"
        />
      </div>

      {/* Table */}
      {loading ? (
        <p>Loading...</p>
      ) : (
        <>
          <table className="border-collapse border w-full">
            <thead>
              <tr className="bg-gray-100">
                <th className="border px-2 py-1">Device ID</th>
                <th className="border px-2 py-1">Timestamp</th>
                <th className="border px-2 py-1">AC Power</th>
                <th className="border px-2 py-1">Module Temp</th>
                <th className="border px-2 py-1">Operational status</th>
              </tr>
            </thead>
            <tbody>
              {paginatedEvents.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-2">
                    No results
                  </td>
                </tr>
              ) : (
                paginatedEvents.map((event, idx) => (
                  <tr key={idx} className="text-center">
                    <td className="border px-2 py-1">{event.device_id}</td>
                    <td className="border px-2 py-1">{event.timestamp}</td>
                    <td className="border px-2 py-1">{event.ac_power}</td>
                    <td className="border px-2 py-1">
                      {event.temperature_module}
                    </td>
                    <td className="border px-2 py-1">
                      {event.status.operational ? "✅" : "❌"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>

          {/* Pagination Controls */}
          <div className="flex justify-center items-center gap-4 mt-4">
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage((p) => p - 1)}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Prev
            </button>
            <span>
              Page {currentPage} of {totalPages}
            </span>
            <button
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage((p) => p + 1)}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
