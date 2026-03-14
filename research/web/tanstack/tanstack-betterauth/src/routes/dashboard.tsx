import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { GitHub } from "~/components/logos/GithubLogo";
import { signOut } from "~/lib/auth-client";
import { getUserId } from "~/lib/auth-server-fn";

export const Route = createFileRoute("/dashboard")({
  component: RouteComponent,
  beforeLoad: async () => {
    const userID = await getUserId();
    return {
      userID,
    };
  },
  loader: async ({ context }) => {
    if (!context.userID) {
      throw redirect({ to: "/" });
    }
    return {
      userID: context.userID,
    };
  },
});

function RouteComponent() {
  const { userID } = Route.useLoaderData();
  const navigate = useNavigate();

  return (
    <div>
      <p>Hello "/dashboard"!</p>
      <p>User ID: {userID}</p>
      {userID && (
        <button
          type="button"
          className="btn"
          onClick={() =>
            signOut({}, { onSuccess: () => navigate({ to: "/" }) })
          }
        >
          <GitHub />
        </button>
      )}
    </div>
  );
}
