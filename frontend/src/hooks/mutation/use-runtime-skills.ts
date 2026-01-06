import { useMutation, useQueryClient } from "@tanstack/react-query";
import { openHands } from "#/api/open-hands-axios";
import { useConversationId } from "../use-conversation-id";

// Runtime Skill Types
export interface RuntimeSkillCreateRequest {
  name: string;
  type: "knowledge" | "repo" | "task";
  content: string;
  triggers?: string[];
  persist?: boolean;
}

export interface RuntimeSkillUpdateRequest {
  content?: string;
  triggers?: string[];
}

export interface RuntimeSkillResponse {
  name: string;
  type: "knowledge" | "repo" | "task";
  content: string;
  triggers: string[];
  source: "runtime" | "file" | "global" | "user" | "repo";
  created_at?: string;
  is_active: boolean;
}

export interface RuntimeSkillsListResponse {
  skills: RuntimeSkillResponse[];
}

/**
 * Hook to create a runtime skill
 */
export const useCreateRuntimeSkill = () => {
  const { conversationId } = useConversationId();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (skill: RuntimeSkillCreateRequest) => {
      if (!conversationId) {
        throw new Error("No conversation ID provided");
      }

      const { data } = await openHands.post<RuntimeSkillResponse>(
        `/api/conversations/${conversationId}/runtime-skills`,
        skill,
      );
      return data;
    },
    onSuccess: () => {
      // Invalidate skills query to refetch the updated list
      if (conversationId) {
        queryClient.invalidateQueries({
          queryKey: ["conversation", conversationId, "skills"],
        });
      }
    },
  });
};

/**
 * Hook to update a runtime skill
 */
export const useUpdateRuntimeSkill = () => {
  const { conversationId } = useConversationId();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      name,
      updates,
    }: {
      name: string;
      updates: RuntimeSkillUpdateRequest;
    }) => {
      if (!conversationId) {
        throw new Error("No conversation ID provided");
      }

      const { data } = await openHands.put<RuntimeSkillResponse>(
        `/api/conversations/${conversationId}/runtime-skills/${name}`,
        updates,
      );
      return data;
    },
    onSuccess: () => {
      // Invalidate skills query to refetch the updated list
      if (conversationId) {
        queryClient.invalidateQueries({
          queryKey: ["conversation", conversationId, "skills"],
        });
      }
    },
  });
};

/**
 * Hook to delete a runtime skill
 */
export const useDeleteRuntimeSkill = () => {
  const { conversationId } = useConversationId();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (name: string) => {
      if (!conversationId) {
        throw new Error("No conversation ID provided");
      }

      await openHands.delete(
        `/api/conversations/${conversationId}/runtime-skills/${name}`,
      );
      return { name };
    },
    onSuccess: () => {
      // Invalidate skills query to refetch the updated list
      if (conversationId) {
        queryClient.invalidateQueries({
          queryKey: ["conversation", conversationId, "skills"],
        });
      }
    },
  });
};

/**
 * Hook to persist a runtime skill to file
 */
export const usePersistRuntimeSkill = () => {
  const { conversationId } = useConversationId();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (name: string) => {
      if (!conversationId) {
        throw new Error("No conversation ID provided");
      }

      const { data } = await openHands.post<{ message: string; path: string }>(
        `/api/conversations/${conversationId}/runtime-skills/${name}/persist`,
      );
      return data;
    },
    onSuccess: () => {
      // Invalidate skills query to refetch the updated list
      if (conversationId) {
        queryClient.invalidateQueries({
          queryKey: ["conversation", conversationId, "skills"],
        });
      }
    },
  });
};
