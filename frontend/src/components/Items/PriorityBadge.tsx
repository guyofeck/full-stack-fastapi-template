import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { ItemPublic } from "@/client"

const PRIORITY_STYLES: Record<string, string> = {
  low: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
  medium:
    "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300",
  high: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300",
}

export function PriorityBadge({ priority }: { priority: ItemPublic["priority"] }) {
  return (
    <Badge variant="outline" className={cn("capitalize", PRIORITY_STYLES[priority])}>
      {priority}
    </Badge>
  )
}
