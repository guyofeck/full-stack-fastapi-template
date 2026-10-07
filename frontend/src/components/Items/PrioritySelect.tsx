import type { ItemPriority } from "@/client"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface PrioritySelectProps {
  value: ItemPriority
  onValueChange: (value: ItemPriority) => void
  onBlur: () => void
  id?: string
  "aria-describedby"?: string
  "aria-invalid"?: boolean
}

export default function PrioritySelect(props: PrioritySelectProps) {
  const { value, onValueChange, ...triggerProps } = props
  return (
    <Select value={value} onValueChange={onValueChange}>
      <SelectTrigger className="w-full" {...triggerProps}>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="low">Low</SelectItem>
        <SelectItem value="medium">Medium</SelectItem>
        <SelectItem value="high">High</SelectItem>
      </SelectContent>
    </Select>
  )
}
