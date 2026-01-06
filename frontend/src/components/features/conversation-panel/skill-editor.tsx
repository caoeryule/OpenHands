import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { I18nKey } from "#/i18n/declaration";
import { Button } from "#/ui/button";
import { Input } from "#/ui/input";
import { Textarea } from "#/ui/textarea";
import { Label } from "#/ui/label";
import { RadioGroup, RadioGroupItem } from "#/ui/radio-group";
import { Badge } from "#/ui/badge";
import { X } from "lucide-react";

type SkillType = "knowledge" | "repo" | "task";

interface SkillEditorProps {
  onSave: (skill: {
    name: string;
    type: SkillType;
    content: string;
    triggers: string[];
    persist: boolean;
  }) => void;
  onCancel: () => void;
  initialSkill?: {
    name: string;
    type: SkillType;
    content: string;
    triggers: string[];
  };
  isEdit?: boolean;
}

export function SkillEditor({
  onSave,
  onCancel,
  initialSkill,
  isEdit = false,
}: SkillEditorProps) {
  const { t } = useTranslation();
  
  const [name, setName] = useState(initialSkill?.name || "");
  const [skillType, setSkillType] = useState<SkillType>(
    initialSkill?.type || "knowledge"
  );
  const [content, setContent] = useState(initialSkill?.content || "");
  const [triggers, setTriggers] = useState<string[]>(
    initialSkill?.triggers || []
  );
  const [currentTrigger, setCurrentTrigger] = useState("");
  const [persist, setPersist] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Validation
  useEffect(() => {
    const newErrors: Record<string, string> = {};

    if (name && !/^[a-zA-Z0-9_-]+$/.test(name)) {
      newErrors.name = "名称只能包含字母、数字、连字符和下划线";
    }
    if (name && name.length < 2) {
      newErrors.name = "名称至少需要2个字符";
    }
    if (name && name.length > 100) {
      newErrors.name = "名称不能超过100个字符";
    }

    if (content && content.length < 10) {
      newErrors.content = "内容至少需要10个字符";
    }
    if (content && content.length > 51200) {
      newErrors.content = "内容不能超过50KB";
    }

    if (skillType !== "repo" && triggers.length === 0) {
      newErrors.triggers = `${
        skillType === "knowledge" ? "知识" : "任务"
      }类型的 Skill 至少需要一个触发词`;
    }

    if (skillType === "repo" && triggers.length > 0) {
      newErrors.triggers = "仓库类型的 Skill 不能有触发词";
    }

    setErrors(newErrors);
  }, [name, skillType, content, triggers]);

  const handleAddTrigger = () => {
    if (currentTrigger.trim() && !triggers.includes(currentTrigger.trim())) {
      let trigger = currentTrigger.trim();
      // For task skills, ensure trigger starts with /
      if (skillType === "task" && !trigger.startsWith("/")) {
        trigger = `/${trigger}`;
      }
      setTriggers([...triggers, trigger]);
      setCurrentTrigger("");
    }
  };

  const handleRemoveTrigger = (triggerToRemove: string) => {
    setTriggers(triggers.filter((t) => t !== triggerToRemove));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddTrigger();
    }
  };

  const handleSave = () => {
    if (Object.keys(errors).length > 0 || !name || !content) {
      return;
    }

    onSave({
      name,
      type: skillType,
      content,
      triggers,
      persist,
    });
  };

  const isValid =
    Object.keys(errors).length === 0 && name.length > 0 && content.length > 0;

  return (
    <div className="flex flex-col gap-4 p-4">
      <h2 className="text-xl font-semibold">
        {isEdit ? "编辑 Skill" : "创建新 Skill"}
      </h2>

      {/* Name Input */}
      <div className="space-y-2">
        <Label htmlFor="skill-name">名称 *</Label>
        <Input
          id="skill-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="skill-name"
          disabled={isEdit}
          className={errors.name ? "border-red-500" : ""}
        />
        {errors.name && (
          <p className="text-sm text-red-500">{errors.name}</p>
        )}
      </div>

      {/* Type Selection */}
      <div className="space-y-2">
        <Label>类型 *</Label>
        <RadioGroup
          value={skillType}
          onValueChange={(value) => setSkillType(value as SkillType)}
          disabled={isEdit}
        >
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="knowledge" id="type-knowledge" />
            <Label htmlFor="type-knowledge" className="font-normal">
              知识型 (Knowledge) - 通过关键词触发
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="task" id="type-task" />
            <Label htmlFor="type-task" className="font-normal">
              任务型 (Task) - 通过命令触发
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="repo" id="type-repo" />
            <Label htmlFor="type-repo" className="font-normal">
              仓库型 (Repository) - 始终激活
            </Label>
          </div>
        </RadioGroup>
      </div>

      {/* Triggers Input (not for repo type) */}
      {skillType !== "repo" && (
        <div className="space-y-2">
          <Label htmlFor="skill-triggers">
            触发词 * {skillType === "task" && "(自动添加 / 前缀)"}
          </Label>
          <div className="flex gap-2">
            <Input
              id="skill-triggers"
              value={currentTrigger}
              onChange={(e) => setCurrentTrigger(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                skillType === "task" ? "/command" : "关键词"
              }
            />
            <Button onClick={handleAddTrigger} variant="outline">
              添加
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            {triggers.map((trigger) => (
              <Badge key={trigger} variant="secondary" className="gap-1">
                {trigger}
                <X
                  className="h-3 w-3 cursor-pointer"
                  onClick={() => handleRemoveTrigger(trigger)}
                />
              </Badge>
            ))}
          </div>
          {errors.triggers && (
            <p className="text-sm text-red-500">{errors.triggers}</p>
          )}
        </div>
      )}

      {/* Content Editor */}
      <div className="space-y-2">
        <Label htmlFor="skill-content">内容 * (Markdown 格式)</Label>
        <Textarea
          id="skill-content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="输入 Skill 的内容，支持 Markdown 格式..."
          className={`min-h-[200px] font-mono ${
            errors.content ? "border-red-500" : ""
          }`}
        />
        <div className="flex justify-between text-sm text-gray-500">
          <span>
            {content.length} / 51200 字符 ({Math.round(content.length / 1024)} KB)
          </span>
          {errors.content && (
            <span className="text-red-500">{errors.content}</span>
          )}
        </div>
      </div>

      {/* Persist Option */}
      {!isEdit && (
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="persist"
            checked={persist}
            onChange={(e) => setPersist(e.target.checked)}
            className="w-4 h-4"
          />
          <Label htmlFor="persist" className="font-normal">
            立即持久化到数据库（保留到会话结束后）
          </Label>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-end gap-2 pt-4 border-t">
        <Button onClick={onCancel} variant="outline">
          取消
        </Button>
        <Button onClick={handleSave} disabled={!isValid}>
          {isEdit ? "更新" : "创建"}
        </Button>
      </div>

      {/* Help Text */}
      <div className="text-sm text-gray-500 space-y-1">
        <p>💡 提示：</p>
        <ul className="list-disc list-inside space-y-1 ml-2">
          <li>知识型 Skill 会在对话中包含触发词时自动激活</li>
          <li>任务型 Skill 需要用 /命令 的格式手动触发</li>
          <li>仓库型 Skill 会在整个会话中始终激活</li>
          <li>运行时 Skill 具有最高优先级，会覆盖同名的其他 Skills</li>
        </ul>
      </div>
    </div>
  );
}
