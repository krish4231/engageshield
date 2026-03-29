interface BadgeProps {
  severity: string;
  children?: React.ReactNode;
}

export default function Badge({ severity, children }: BadgeProps) {
  return (
    <span className={`badge badge-${severity}`}>
      {children || severity}
    </span>
  );
}
