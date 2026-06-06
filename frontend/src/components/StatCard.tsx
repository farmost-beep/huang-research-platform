interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: string;
}

export default function StatCard({ title, value, subtitle, icon }: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider">{title}</p>
          <p className="text-2xl font-bold text-white mt-1">
            {value}
            {subtitle && <span className="text-sm font-normal text-gray-500 ml-1">{subtitle}</span>}
          </p>
        </div>
        {icon && <span className="text-2xl opacity-60">{icon}</span>}
      </div>
    </div>
  );
}
