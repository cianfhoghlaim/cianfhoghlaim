import { createFileRoute, Link } from "@tanstack/react-router";
import { signIn, signOut, useSession } from "~/lib/auth-client";

export const Route = createFileRoute("/")({
  component: Home,
});

function Home() {
  const { data: session } = useSession();

  return (
    <div>
      {!session && (
        <button
          type="button"
          className="btn"
          onClick={() => signIn.social({ provider: "github" })}
        >
          Sign In
        </button>
      )}
      {session && (
        <div className="flex flex-col items-center">
          <Link to="/dashboard">Dashboard</Link>
          <p>Welcome, {session.user.name}!</p>
          <button type="button" className="btn" onClick={() => signOut()}>
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
}
