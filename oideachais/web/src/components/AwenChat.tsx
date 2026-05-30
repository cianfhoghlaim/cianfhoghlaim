import { CopilotPopup } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

export function AwenChat() {
  return (
    <CopilotPopup
      instructions="You are Awen, an AI assistant built on Agno and Google ADK. You help users navigate the Celtic MMO educational platform. You can render Generative UI components."
      labels={{
        title: "Awen Assistant",
        initial: "Fáilte! How can I assist you with your learning journey today?"
      }}
      defaultOpen={false}
    />
  );
}
