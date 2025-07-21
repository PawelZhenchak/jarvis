import { CustomSidebar } from './custom-sidebar';

export function ChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen w-full">
      <CustomSidebar />
      <div className="flex flex-col flex-1">
        <header className="flex items-center justify-center p-4 h-20 bg-transparent">
          <h1 className="text-2xl font-bold tracking-wider text-white">NOWY CZAT</h1>
        </header>
        <main className="flex-1 bg-card/50 backdrop-blur-sm rounded-tl-3xl overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  );
}
