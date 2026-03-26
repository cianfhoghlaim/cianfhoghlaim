import { createFileRoute } from "@tanstack/react-router";
import { useCoAgent } from "@copilotkit/react-core";
import { BookOpen, FileText, Search, TrendingUp } from "lucide-react";

export const Route = createFileRoute("/")({
  component: DashboardPage,
});

function DashboardPage() {
  // Connect to the education assistant agent
  const { state } = useCoAgent({
    name: "education_assistant",
    initialState: {
      recentSearches: [] as string[],
      indexingProgress: null as null | { current: number; total: number },
    },
  });

  return (
    <div className="space-y-8">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={<FileText className="h-6 w-6 text-blue-600" />}
          title="Curriculum Documents"
          value="1,892"
          description="Indexed from curriculumonline.ie"
        />
        <StatCard
          icon={<BookOpen className="h-6 w-6 text-green-600" />}
          title="Examiner Reports"
          value="200+"
          description="From examinations.ie"
        />
        <StatCard
          icon={<Search className="h-6 w-6 text-purple-600" />}
          title="Search Index"
          value="Active"
          description="LanceDB + hybrid search"
        />
        <StatCard
          icon={<TrendingUp className="h-6 w-6 text-orange-600" />}
          title="Embeddings"
          value="384-dim"
          description="Multilingual MiniLM"
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <QuickAction
            href="/search"
            title="Search Curriculum"
            description="Search curriculum specifications, syllabi, and guidelines"
          />
          <QuickAction
            href="/search?type=examiner_report"
            title="Examiner Reports"
            description="Find SEC examiner reports and recommendations"
          />
          <QuickAction
            href="/search?level=junior_cycle"
            title="Junior Cycle"
            description="Browse Junior Cycle curriculum materials"
          />
        </div>
      </div>

      {/* Education Levels */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Education Levels
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <LevelCard
            title="Primary"
            description="Junior Infants to 6th Class"
            subjects={["English", "Irish", "Mathematics", "SESE"]}
          />
          <LevelCard
            title="Junior Cycle"
            description="1st to 3rd Year"
            subjects={["English", "Irish", "Maths", "Science"]}
          />
          <LevelCard
            title="Transition Year"
            description="4th Year"
            subjects={["Optional modules", "Work experience"]}
          />
          <LevelCard
            title="Senior Cycle"
            description="5th & 6th Year - Leaving Cert"
            subjects={["Core subjects", "Electives"]}
          />
        </div>
      </div>

      {/* Indexing Progress */}
      {state?.indexingProgress && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-900">
              Indexing in progress...
            </span>
            <span className="text-sm text-blue-700">
              {state.indexingProgress.current} / {state.indexingProgress.total}
            </span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{
                width: `${(state.indexingProgress.current / state.indexingProgress.total) * 100}%`,
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({
  icon,
  title,
  value,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  value: string;
  description: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className="flex-shrink-0">{icon}</div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          <p className="text-xs text-gray-400">{description}</p>
        </div>
      </div>
    </div>
  );
}

function QuickAction({
  href,
  title,
  description,
}: {
  href: string;
  title: string;
  description: string;
}) {
  return (
    <a
      href={href}
      className="block p-4 border rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
    >
      <h3 className="font-medium text-gray-900">{title}</h3>
      <p className="text-sm text-gray-500">{description}</p>
    </a>
  );
}

function LevelCard({
  title,
  description,
  subjects,
}: {
  title: string;
  description: string;
  subjects: string[];
}) {
  return (
    <div className="border rounded-lg p-4">
      <h3 className="font-medium text-gray-900">{title}</h3>
      <p className="text-sm text-gray-500 mb-2">{description}</p>
      <div className="flex flex-wrap gap-1">
        {subjects.map((subject) => (
          <span
            key={subject}
            className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
          >
            {subject}
          </span>
        ))}
      </div>
    </div>
  );
}
