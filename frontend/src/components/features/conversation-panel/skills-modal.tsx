import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Plus } from "lucide-react";
import { ModalBackdrop } from "#/components/shared/modals/modal-backdrop";
import { ModalBody } from "#/components/shared/modals/modal-body";
import { I18nKey } from "#/i18n/declaration";
import { useConversationSkills } from "#/hooks/query/use-conversation-skills";
import { AgentState } from "#/types/agent-state";
import { Typography } from "#/ui/typography";
import { Button } from "#/ui/button";
import { SkillsModalHeader } from "./skills-modal-header";
import { SkillsLoadingState } from "./skills-loading-state";
import { SkillsEmptyState } from "./skills-empty-state";
import { SkillItem } from "./skill-item";
import { SkillEditor } from "./skill-editor";
import { useAgentState } from "#/hooks/use-agent-state";
import {
  useCreateRuntimeSkill,
  useUpdateRuntimeSkill,
  useDeleteRuntimeSkill,
  usePersistRuntimeSkill,
  RuntimeSkillCreateRequest,
} from "#/hooks/mutation/use-runtime-skills";
import { Skill } from "#/api/conversation-service/v1-conversation-service.types";
import { Microagent } from "#/api/open-hands.types";

interface SkillsModalProps {
  onClose: () => void;
}

export function SkillsModal({ onClose }: SkillsModalProps) {
  const { t } = useTranslation();
  const { curAgentState } = useAgentState();
  const [expandedAgents, setExpandedAgents] = useState<Record<string, boolean>>(
    {},
  );
  const [isCreating, setIsCreating] = useState(false);
  const [editingSkill, setEditingSkill] = useState<Skill | Microagent | null>(
    null,
  );
  const {
    data: skills,
    isLoading,
    isError,
    refetch,
    isRefetching,
  } = useConversationSkills();

  // Runtime skills mutation hooks
  const createSkill = useCreateRuntimeSkill();
  const updateSkill = useUpdateRuntimeSkill();
  const deleteSkill = useDeleteRuntimeSkill();
  const persistSkill = usePersistRuntimeSkill();

  const toggleAgent = (agentName: string) => {
    setExpandedAgents((prev) => ({
      ...prev,
      [agentName]: !prev[agentName],
    }));
  };

  const isAgentReady = ![AgentState.LOADING, AgentState.INIT].includes(
    curAgentState,
  );

  const handleCreateSkill = async (skillData: RuntimeSkillCreateRequest) => {
    try {
      await createSkill.mutateAsync(skillData);
      setIsCreating(false);
    } catch (error) {
      console.error("Failed to create skill:", error);
      throw error;
    }
  };

  const handleUpdateSkill = async (skillData: RuntimeSkillCreateRequest) => {
    if (!editingSkill) return;

    try {
      await updateSkill.mutateAsync({
        name: editingSkill.name,
        updates: {
          content: skillData.content,
          triggers: skillData.triggers,
        },
      });
      setEditingSkill(null);
    } catch (error) {
      console.error("Failed to update skill:", error);
      throw error;
    }
  };

  const handleDeleteSkill = async (name: string) => {
    if (!confirm(`Are you sure you want to delete the skill "${name}"?`)) {
      return;
    }

    try {
      await deleteSkill.mutateAsync(name);
    } catch (error) {
      console.error("Failed to delete skill:", error);
    }
  };

  const handlePersistSkill = async (name: string) => {
    try {
      const result = await persistSkill.mutateAsync(name);
      alert(`Skill persisted successfully to ${result.path}`);
    } catch (error) {
      console.error("Failed to persist skill:", error);
    }
  };

  // Check if a skill is editable (runtime source)
  const isSkillEditable = (skill: Skill | Microagent) => {
    if ("source" in skill) {
      return skill.source === "runtime";
    }
    return false;
  };

  // Show editor if creating or editing
  if (isCreating || editingSkill) {
    return (
      <ModalBackdrop onClose={onClose}>
        <ModalBody width="medium" className="max-h-[80vh] flex flex-col">
          <Typography.H2 className="mb-4">
            {isCreating ? "Create New Skill" : "Edit Skill"}
          </Typography.H2>
          <SkillEditor
            onSave={isCreating ? handleCreateSkill : handleUpdateSkill}
            onCancel={() => {
              setIsCreating(false);
              setEditingSkill(null);
            }}
            initialSkill={
              editingSkill
                ? {
                    name: editingSkill.name,
                    type: editingSkill.type as "knowledge" | "repo" | "task",
                    content: editingSkill.content,
                    triggers: editingSkill.triggers || [],
                  }
                : undefined
            }
            isEdit={!!editingSkill}
          />
        </ModalBody>
      </ModalBackdrop>
    );
  }

  return (
    <ModalBackdrop onClose={onClose}>
      <ModalBody
        width="medium"
        className="max-h-[80vh] flex flex-col items-start"
        testID="skills-modal"
      >
        <div className="w-full flex items-center justify-between mb-2">
          <SkillsModalHeader
            isAgentReady={isAgentReady}
            isLoading={isLoading}
            isRefetching={isRefetching}
            onRefresh={refetch}
          />
          {isAgentReady && (
            <Button
              onClick={() => setIsCreating(true)}
              className="flex items-center gap-2"
              size="sm"
            >
              <Plus size={16} />
              Create Skill
            </Button>
          )}
        </div>

        {isAgentReady && (
          <Typography.Text className="text-sm text-gray-400">
            {t(I18nKey.SKILLS_MODAL$WARNING)}
          </Typography.Text>
        )}

        <div className="w-full h-[60vh] overflow-auto rounded-md custom-scrollbar-always">
          {!isAgentReady && (
            <div className="w-full h-full flex items-center text-center justify-center text-2xl text-tertiary-light">
              <Typography.Text>
                {t(I18nKey.DIFF_VIEWER$WAITING_FOR_RUNTIME)}
              </Typography.Text>
            </div>
          )}

          {isLoading && <SkillsLoadingState />}

          {!isLoading &&
            isAgentReady &&
            (isError || !skills || skills.length === 0) && (
              <SkillsEmptyState isError={isError} />
            )}

          {!isLoading && isAgentReady && skills && skills.length > 0 && (
            <div className="p-2 space-y-3">
              {skills.map((skill) => {
                const isExpanded = expandedAgents[skill.name] || false;
                const editable = isSkillEditable(skill);

                return (
                  <SkillItem
                    key={skill.name}
                    skill={skill}
                    isExpanded={isExpanded}
                    onToggle={toggleAgent}
                    editable={editable}
                    onEdit={
                      editable ? () => setEditingSkill(skill) : undefined
                    }
                    onDelete={
                      editable ? () => handleDeleteSkill(skill.name) : undefined
                    }
                    onPersist={
                      editable
                        ? () => handlePersistSkill(skill.name)
                        : undefined
                    }
                  />
                );
              })}
            </div>
          )}
        </div>
      </ModalBody>
    </ModalBackdrop>
  );
}
