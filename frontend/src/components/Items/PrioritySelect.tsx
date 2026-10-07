import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { Priority } from "@/client"

const PRIORITY_OPTIONS: Priority[] = ["low", "medium", "high"]

export function PrioritySelect({
  value,
  onChange,
}: {
  value: Priority
  onChange: (value: Priority) => void
}) {
  return (
    <Select value={value} onValueChange={(v) => onChange(v as Priority)}>
      <SelectTrigger className="w-full">
        <SelectValue placeholder="Select priority" />
      </SelectTrigger>
      <SelectContent>
        {PRIORITY_OPTIONS.map((p) => (
          <SelectItem key={p} value={p} className="capitalize">
            {p}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
