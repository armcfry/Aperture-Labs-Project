/**
 * Page for viewing the result of an inspection.
 * @param id - The inspection ID
 */

export default async function InspectResultPage(
    { params }: { params: Promise<{ id: string } | undefined> }
) {
    const { id } = (await params) ?? { id: "" };
    if (!id) {
        return <div>No ID provided</div>;
    }
    return <div>Inspecting result: {id}</div>;
}