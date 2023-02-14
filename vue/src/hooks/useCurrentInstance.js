import { getCurrentInstance } from 'vue';
export default function useCurrentInstance() {
  const { appContext } = getCurrentInstance();
  const globalProperties = appContext.config.globalProperties;
  return {
    globalProperties,
  };
}
