import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "danger";

export function Button({
  variant = "primary", className = "", ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  const base = "px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed";
  const styles: Record<Variant, string> = {
    primary: "bg-ochre text-white hover:bg-ochre/90",
    secondary: "border border-ink/30 text-ink hover:bg-ink/5",
    danger: "border border-danger text-danger hover:bg-danger/10",
  };
  return <button {...props} className={`${base} ${styles[variant]} ${className}`} />;
}
