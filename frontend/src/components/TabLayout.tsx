interface TabLayoutProps {
  title: string;
  instructions: string[];
  children: React.ReactNode;
}

export function TabLayout({ title, instructions, children }: TabLayoutProps) {
  return (
    <div className="tab-layout">
      <aside className="sidebar">
        <h3>{title}</h3>
        <ul>
          {instructions.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </aside>
      <div className="tab-content">{children}</div>
    </div>
  );
}
