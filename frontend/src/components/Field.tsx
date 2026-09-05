import { InputHTMLAttributes, SelectHTMLAttributes, ReactNode } from "react";

export function Field({
  label, children,
}: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm text-olive">{label}</span>
      {children}
    </label>
  );
}

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={`w-full border border-line bg-white px-3 py-2 text-sm text-ink focus:border-ochre focus:outline-none ${props.className ?? ""}`}
    />
  );
}

export function Select({ children, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...props}
      className={`w-full border border-line bg-white px-3 py-2 text-sm text-ink focus:border-ochre focus:outline-none ${props.className ?? ""}`}
    >
      {children}
    </select>
  );
}
