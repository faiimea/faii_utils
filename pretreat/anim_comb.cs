using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
public class TempData
{
    public List<Keyframe> Keyframes = new List<Keyframe>();
    public EditorCurveBinding Binding;
}
public class AnimationClipMerger : MonoBehaviour
{
    [MenuItem("MyMenu/Merge Animation Clips")]

    static void MergeClips()
    {
        Debug.Log("Now time 2");
        // 指定包含动画剪辑的文件夹路径
        string folderPath = "Assets/A"; // 替换为实际的文件夹路径

        // 获取指定文件夹中的所有动画剪辑
        string[] clipGuids = AssetDatabase.FindAssets("t:AnimationClip", new[] { folderPath });
        AnimationClip[] sourceClips = new AnimationClip[clipGuids.Length];
        for (int i = 0; i < clipGuids.Length; i++)
        {
            string clipPath = AssetDatabase.GUIDToAssetPath(clipGuids[i]);
            sourceClips[i] = AssetDatabase.LoadAssetAtPath<AnimationClip>(clipPath);
        }

        // 创建一个新的Animation Clip
        AnimationClip newClip = new AnimationClip();
        newClip.name = "MergedClip";

        foreach (var clip in sourceClips)
        {
            Debug.Log($"Clip Name: {clip.name}, Length: {clip.length}");
        }
        newClip.frameRate = sourceClips.Length > 0 ? sourceClips[0].frameRate : 30; // 设置帧率，你可以根据实际情况调整
        MergeAnimationClips(sourceClips);
        return;
    }

    public static void MergeAnimationClips(AnimationClip[] sourceClips)
    {
        AnimationClip newClip = new AnimationClip();
        newClip.name = "MergedClip";
        newClip.frameRate = sourceClips.Length > 0 ? sourceClips[0].frameRate : 30; // 设置帧率，你可以根据实际情况调整

        // 复制每个源片段的曲线到新片段中
        float currentTime = 0f;
        Dictionary<string, TempData> bindingMap = new Dictionary<string, TempData>();
        foreach (var clip in sourceClips)
        {
            EditorCurveBinding[] curveBindings = AnimationUtility.GetCurveBindings(clip);
            foreach (var binding in curveBindings)
            {
                AnimationCurve curve = AnimationUtility.GetEditorCurve(clip, binding);
                Keyframe[] keyframes = curve.keys;
                Keyframe[] newKeyframes = new Keyframe[keyframes.Length];
                string properName = $"{binding.path}/{binding.propertyName}";
                if (!bindingMap.ContainsKey(properName))
                {
                    bindingMap.Add(properName, new TempData() { Binding = binding });
                }
                for (int i = 0; i < keyframes.Length; i++)
                {
                    newKeyframes[i] = new Keyframe(keyframes[i].time + currentTime, keyframes[i].value);
                }
                bindingMap[properName].Keyframes.AddRange(newKeyframes);
            }
            currentTime += clip.length;
            currentTime += 0.041667f;
        }
        foreach (var item in bindingMap)
        {
            AnimationCurve animationCurve = new AnimationCurve(item.Value.Keyframes.ToArray());
            AnimationUtility.SetEditorCurve(newClip, item.Value.Binding, animationCurve);
        }
        // 保存新片段
        AssetDatabase.CreateAsset(newClip, "Assets/A/NewMergedClip.anim"); // 替换为保存的路径

        Debug.Log("Animation Clips merged and saved as NewMergedClip.anim");
    }
}
