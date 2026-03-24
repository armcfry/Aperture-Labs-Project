/**
 * Tests for requirements:
 * - Req 3: Upload feature shall allow uploading of multiple design specifications per project
 * - Req 12: Front End system shall group uploaded artifacts by project
 * - Req 13: Front End system shall allow users to create projects with design specifications
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";

// --- Mocks ---
const mockPush = vi.fn();
const mockReplace = vi.fn();
vi.mock("next/navigation", () => ({
    useRouter: () => ({ push: mockPush, replace: mockReplace }),
}));

const mockSetCurrentProject = vi.fn();
vi.mock("@/app/AppProvider", () => ({
    useApp: () => ({
        user: { id: "user-1", email: "test@example.com" },
        hasRestoredFromStorage: true,
        setCurrentProject: mockSetCurrentProject,
    }),
}));

const mockListProjects = vi.fn();
const mockListDesignSpecs = vi.fn();
const mockCreateProject = vi.fn();
const mockUploadDesignSpec = vi.fn();
const mockArchiveProject = vi.fn();
const mockDeleteProject = vi.fn();

vi.mock("@/lib/api", async (importOriginal) => {
    const actual = await importOriginal<typeof import("@/lib/api")>();
    return {
        ...actual,
        listProjects: (...args: unknown[]) => mockListProjects(...args),
        listDesignSpecs: (...args: unknown[]) => mockListDesignSpecs(...args),
        createProject: (...args: unknown[]) => mockCreateProject(...args),
        uploadDesignSpec: (...args: unknown[]) => mockUploadDesignSpec(...args),
        archiveProject: (...args: unknown[]) => mockArchiveProject(...args),
        deleteProject: (...args: unknown[]) => mockDeleteProject(...args),
        API_BASE_URL: "http://localhost:8000",
    };
});

vi.mock("@/components/DesignSpecPreview", () => ({
    default: () => <div data-testid="design-spec-preview" />,
}));
vi.mock("@/components/DesignSpecLink", () => ({
    DesignSpecLink: ({ spec }: { spec: string }) => <span>{spec}</span>,
}));

import ProjectsPage from "@/app/projects/page";

type ApiProject = {
    id: string;
    name: string;
    created_at: string;
    updated_at: string;
    archived_at?: string | null;
};

function makeApiProject(overrides: Partial<ApiProject> = {}): ApiProject {
    return {
        id: "proj-1",
        name: "My Project",
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
        archived_at: null,
        ...overrides,
    };
}

function makeSpecFile(name = "spec.pdf"): File {
    return new File(["pdf content"], name, { type: "application/pdf" });
}

describe("ProjectsPage — Req 13: create projects", () => {
    beforeEach(() => {
        mockListProjects.mockReset();
        mockListDesignSpecs.mockReset();
        mockCreateProject.mockReset();
        mockUploadDesignSpec.mockReset();
        mockPush.mockReset();
        mockSetCurrentProject.mockReset();

        // Default: no existing projects → show create form directly
        mockListProjects.mockResolvedValue([]);
        mockListDesignSpecs.mockResolvedValue([]);
    });

    it("shows the create project form when no projects exist", async () => {
        render(<ProjectsPage />);
        await waitFor(() => expect(screen.getByText(/create a new project/i)).toBeInTheDocument());
        expect(screen.getByPlaceholderText(/circuit board/i)).toBeInTheDocument();
    });

    it("Create Project button is disabled when name is empty", async () => {
        render(<ProjectsPage />);
        await waitFor(() => expect(screen.getByRole("button", { name: /create project/i })).toBeInTheDocument());
        expect(screen.getByRole("button", { name: /create project/i })).toBeDisabled();
    });

    it("Create Project button is disabled when name is filled but no spec is uploaded", async () => {
        render(<ProjectsPage />);
        await waitFor(() => expect(screen.getByPlaceholderText(/circuit board/i)).toBeInTheDocument());
        await userEvent.type(screen.getByPlaceholderText(/circuit board/i), "My Project");
        expect(screen.getByRole("button", { name: /create project/i })).toBeDisabled();
    });

    it("Create Project button is enabled when name and at least one spec are provided", async () => {
        render(<ProjectsPage />);
        await waitFor(() => expect(screen.getByPlaceholderText(/circuit board/i)).toBeInTheDocument());
        await userEvent.type(screen.getByPlaceholderText(/circuit board/i), "My Project");

        const specInput = screen.getByLabelText(/drop files here/i) as HTMLInputElement;
        await userEvent.upload(specInput, makeSpecFile("spec.pdf"));

        expect(screen.getByRole("button", { name: /create project/i })).not.toBeDisabled();
    });

    it("calls createProject then uploadDesignSpec for each file on submit", async () => {
        mockCreateProject.mockResolvedValue(makeApiProject({ id: "new-proj" }));
        mockUploadDesignSpec.mockResolvedValue({ filename: "spec.pdf", project_id: "new-proj", object_key: "k" });

        render(<ProjectsPage />);
        await waitFor(() => expect(screen.getByPlaceholderText(/circuit board/i)).toBeInTheDocument());

        await userEvent.type(screen.getByPlaceholderText(/circuit board/i), "My Project");
        const specInput = screen.getByLabelText(/drop files here/i) as HTMLInputElement;
        await userEvent.upload(specInput, [makeSpecFile("a.pdf"), makeSpecFile("b.pdf")]);
        await userEvent.click(screen.getByRole("button", { name: /create project/i }));

        await waitFor(() => expect(mockCreateProject).toHaveBeenCalledWith({ name: "My Project" }));
        await waitFor(() => expect(mockUploadDesignSpec).toHaveBeenCalledTimes(2));
    });

    it("navigates to /inspect after successful project creation", async () => {
        mockCreateProject.mockResolvedValue(makeApiProject({ id: "new-proj" }));
        mockUploadDesignSpec.mockResolvedValue({ filename: "spec.pdf", project_id: "new-proj", object_key: "k" });

        render(<ProjectsPage />);
        await waitFor(() => expect(screen.getByPlaceholderText(/circuit board/i)).toBeInTheDocument());

        await userEvent.type(screen.getByPlaceholderText(/circuit board/i), "My Project");
        const specInput = screen.getByLabelText(/drop files here/i) as HTMLInputElement;
        await userEvent.upload(specInput, makeSpecFile("spec.pdf"));
        await userEvent.click(screen.getByRole("button", { name: /create project/i }));

        await waitFor(() => expect(mockPush).toHaveBeenCalledWith("/inspect"));
    });
});

describe("ProjectsPage — Req 3: multiple design specs upload", () => {
    beforeEach(() => {
        mockListProjects.mockResolvedValue([]);
        mockListDesignSpecs.mockResolvedValue([]);
        mockCreateProject.mockReset();
        mockUploadDesignSpec.mockReset();
    });

    it("design spec file input has multiple attribute", async () => {
        render(<ProjectsPage />);
        await waitFor(() => expect(screen.getByLabelText(/drop files here/i)).toBeInTheDocument());
        const specInput = screen.getByLabelText(/drop files here/i) as HTMLInputElement;
        expect(specInput).toHaveAttribute("multiple");
    });

    it("selecting multiple spec files shows each filename", async () => {
        render(<ProjectsPage />);
        await waitFor(() => expect(screen.getByLabelText(/drop files here/i)).toBeInTheDocument());

        const specInput = screen.getByLabelText(/drop files here/i) as HTMLInputElement;
        await userEvent.upload(specInput, [makeSpecFile("spec-a.pdf"), makeSpecFile("spec-b.pdf")]);

        expect(screen.getByText("spec-a.pdf")).toBeInTheDocument();
        expect(screen.getByText("spec-b.pdf")).toBeInTheDocument();
    });

    it("uploadDesignSpec is called once per spec file submitted", async () => {
        mockCreateProject.mockResolvedValue(makeApiProject({ id: "proj-x" }));
        mockUploadDesignSpec.mockResolvedValue({ filename: "s.pdf", project_id: "proj-x", object_key: "k" });

        render(<ProjectsPage />);
        await waitFor(() => expect(screen.getByPlaceholderText(/circuit board/i)).toBeInTheDocument());
        await userEvent.type(screen.getByPlaceholderText(/circuit board/i), "P");

        const specInput = screen.getByLabelText(/drop files here/i) as HTMLInputElement;
        await userEvent.upload(specInput, [makeSpecFile("a.pdf"), makeSpecFile("b.pdf"), makeSpecFile("c.pdf")]);
        await userEvent.click(screen.getByRole("button", { name: /create project/i }));

        await waitFor(() => expect(mockUploadDesignSpec).toHaveBeenCalledTimes(3));
    });
});

describe("ProjectsPage — Req 12: group artifacts by project", () => {
    beforeEach(() => {
        mockListDesignSpecs.mockReset();
        mockListProjects.mockReset();
        mockPush.mockReset();
    });

    it("renders each project as its own separate card", async () => {
        mockListProjects.mockResolvedValue([
            makeApiProject({ id: "p1", name: "Alpha Project" }),
            makeApiProject({ id: "p2", name: "Beta Project" }),
        ]);
        mockListDesignSpecs.mockImplementation((id: string) => {
            if (id === "p1") return Promise.resolve(["alpha-spec.pdf"]);
            if (id === "p2") return Promise.resolve(["beta-spec.pdf"]);
            return Promise.resolve([]);
        });

        render(<ProjectsPage />);
        await waitFor(() => expect(screen.getByText("Alpha Project")).toBeInTheDocument());
        expect(screen.getByText("Beta Project")).toBeInTheDocument();
    });

    it("archived projects show an 'Archived' badge", async () => {
        mockListProjects.mockResolvedValue([
            makeApiProject({ id: "p1", name: "Old Project", archived_at: "2026-01-15T00:00:00Z" }),
        ]);
        mockListDesignSpecs.mockResolvedValue([]);

        render(<ProjectsPage />);
        // Switch to "All" tab so archived projects are visible
        await waitFor(() => expect(screen.getByRole("button", { name: /^all$/i })).toBeInTheDocument());
        await userEvent.click(screen.getByRole("button", { name: /^all$/i }));
        await waitFor(() => expect(screen.getByText("Old Project")).toBeInTheDocument());
        expect(screen.getByText("Archived")).toBeInTheDocument();
    });

    it("filter tabs exist for active, archived, and all", async () => {
        mockListProjects.mockResolvedValue([makeApiProject()]);
        mockListDesignSpecs.mockResolvedValue([]);

        render(<ProjectsPage />);
        await waitFor(() => expect(screen.getByRole("button", { name: /^active$/i })).toBeInTheDocument());
        expect(screen.getByRole("button", { name: /^archived$/i })).toBeInTheDocument();
        expect(screen.getByRole("button", { name: /^all$/i })).toBeInTheDocument();
    });

    it("clicking 'archived' filter hides active projects and shows archived ones", async () => {
        mockListProjects.mockResolvedValue([
            makeApiProject({ id: "p1", name: "Active Project", archived_at: null }),
            makeApiProject({ id: "p2", name: "Archived Project", archived_at: "2026-01-15T00:00:00Z" }),
        ]);
        mockListDesignSpecs.mockResolvedValue([]);

        render(<ProjectsPage />);
        await waitFor(() => expect(screen.getByText("Active Project")).toBeInTheDocument());

        await userEvent.click(screen.getByRole("button", { name: /^archived$/i }));

        expect(screen.queryByText("Active Project")).not.toBeInTheDocument();
        expect(screen.getByText("Archived Project")).toBeInTheDocument();
    });

    it("clicking 'all' filter shows both active and archived projects", async () => {
        mockListProjects.mockResolvedValue([
            makeApiProject({ id: "p1", name: "Active Project", archived_at: null }),
            makeApiProject({ id: "p2", name: "Archived Project", archived_at: "2026-01-15T00:00:00Z" }),
        ]);
        mockListDesignSpecs.mockResolvedValue([]);

        render(<ProjectsPage />);
        await waitFor(() => expect(screen.getByText("Active Project")).toBeInTheDocument());

        await userEvent.click(screen.getByRole("button", { name: /^all$/i }));

        expect(screen.getByText("Active Project")).toBeInTheDocument();
        expect(screen.getByText("Archived Project")).toBeInTheDocument();
    });
});
