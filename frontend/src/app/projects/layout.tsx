import Sidebar from '@/components/layout/Sidebar';

export default function ProjectsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden bg-gray-50 w-full lg:w-auto">
        <div className="pt-16 lg:pt-0 flex-1 overflow-hidden">
          {children}
        </div>
      </main>
    </div>
  );
}
