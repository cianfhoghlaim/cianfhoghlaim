from coordinator import run_deep_research
from dotenv import load_dotenv

def main():
    load_dotenv()
    user_query = input("Enter your research query: ")
    result = run_deep_research(user_query)
    with open("research_result.md", "w") as f:
        f.write(result)

    print("Research result saved to research_result.md")


if __name__ == "__main__":
    main()
