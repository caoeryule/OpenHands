import { ChevronDown, ChevronRight, Edit2, Trash2, Save } from "lucide-react";
import { Typography } from "#/ui/typography";
import { Button } from "#/ui/button";
import { SkillTriggers } from "./skill-triggers";
import { SkillContent } from "./skill-content";
import { Skill } from "#/api/conversation-service/v1-conversation-service.types";
import { Microagent } from "#/api/open-hands.types";

interface SkillItemProps {
  skill: Skill | Microagent;
  isExpanded: boolean;
  onToggle: (agentName: string) => void;
  editable?: boolean;
  onEdit?: () => void;
  onDelete?: () => void;
  onPersist?: () => void;
}

export function SkillItem({
  skill,
  isExpanded,
  onToggle,
  editable = false,
  onEdit,
  onDelete,
  onPersist,
}: SkillItemProps) {
  // Get skill source for display
  const skillSource =
    "source" in skill
      ? skill.source
      : ("type" in skill ? "file" : "unknown");

  // Get display type
  const getTypeDisplay = () => {
    if (skill.type === "repo") return "Repository";
    if (skill.type === "knowledge") return "Knowledge";
    if (skill.type === "task") return "Task";
    return skill.type;
  };

  // Get source badge color
  const getSourceColor = () => {
    if (skillSource === "runtime") return "bg-blue-600";
    if (skillSource === "repo") return "bg-green-600";
    if (skillSource === "user") return "bg-purple-600";
    return "bg-gray-800";
  };
  return (
    <div className="rounded-md overflow-hidden">
      <button
        type="button"
        onClick={() => onToggle(skill.name)}
        className="w-full py-3 px-2 text-left flex items-center justify-between hover:bg-gray-700 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Typography.Text className="font-bold text-gray-100">
            {skill.name}
          </Typography.Text>
          {editable && (
            <Typography.Text className="px-2 py-0.5 text-xs rounded-full bg-blue-600 text-white">
              Runtime
            </Typography.Text>
          )}
        </div>
        <div className="flex items-center gap-2">
          {editable && (
            <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
              {onEdit && (
                <Button
                  onClick={onEdit}
                  variant="ghost"
                  size="sm"
                  className="h-7 w-7 p-0"
                  title="Edit skill"
                >
                  <Edit2 size={14} />
                </Button>
              )}
              {onPersist && (
                <Button
                  onClick={onPersist}
                  variant="ghost"
                  size="sm"
                  className="h-7 w-7 p-0"
                  title="Save to file"
                >
                  <Save size={14} />
                </Button>
              )}
              {onDelete && (
                <Button
                  onClick={onDelete}
                  variant="ghost"
                  size="sm"
                  className="h-7 w-7 p-0 text-red-400 hover:text-red-300"
                  title="Delete skill"
                >
                  <Trash2 size={14} />
                </Button>
              )}
            </div>
          )}
          <Typography.Text
            className={`px-2 py-1 text-xs rounded-full ${getSourceColor()} mr-2`}
          >
            {getTypeDisplay()}
          </Typography.Text>
          <Typography.Text className="text-gray-300">
            {isExpanded ? (
              <ChevronDown size={18} />
            ) : (
              <ChevronRight size={18} />
            )}
          </Typography.Text>
        </div>
      </button>

      {isExpanded && (
        <div className="px-2 pb-3 pt-1">
          <SkillTriggers triggers={skill.triggers} />
          <SkillContent content={skill.content} />
        </div>
      )}
    </div>
  );
}
