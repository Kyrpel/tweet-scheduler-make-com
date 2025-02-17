// Export the hooks data directly
export const HOOK_CATEGORIES = {
    "question": {
        "title": "Question Hooks",
        "examples": [
            "So I asked, 'What's the best way to {outcome}?'",
            "Want to {outcome}? Here's how...",
            "How do you {action} that {outcome}?",
            "You don't {outcome} based on {common activity}?",
            "If you want to {outcome}, this thread shares {number} ways to do it:",
            "If you suffer from {pain_point}... I eventually overcame it. {number} things happened:",
            "Want to {outcome}? {action}. This is a small change that can make a huge difference."
        ]
    },
    "challenge": {
        "title": "Challenge Common Beliefs",
        "examples": [
            "{common_belief} Wrong. {topic} can totally change your life.",
            "Most people are trying to {outcome} the hard way. Here's the easy way...",
            "You don't {outcome} based on {common activity}...",
            "{niche} is super competitive. But with the proper system, you can stand out.",
            "{skill} is a superpower. It's the key to {outcome}",
            "{skill} gives you competitive advantage. But most things you've been told are lies.",
            "These are the {number} lies you were told about {topic}"
        ]
    },
    "story": {
        "title": "Story Hooks",
        "examples": [
            "I failed to {action} 3 times. Then I tried this...",
            "In {time_period}, I went from {past} to {present}...",
            "Here's how I {outcome} with ZERO experience...",
            "I spent {amount} on {tools} in the past {time_period}",
            "I've been {doing_what} for {time_period}. This is the advice I'd give myself.",
            "The single best thing I've done in my life: {achievement}",
            "{platform} allowed me to 10x my {outcome}"
        ]
    },
    "authority": {
        "title": "Authority Hooks",
        "examples": [
            "I studied the top {number} {experts} in {field}...",
            "In a rare {expert} interview, they revealed...",
            "{expert} turned {small} into {big}...",
            "Leading experts reveal the truth about {topic}...",
            "New research shows surprising facts about {topic}...",
            "Industry insiders share game-changing insights on {topic}...",
            "The KING of {platform}: {expert_name}. Over the {time_period}, they've {achievement}"
        ]
    },
    "stats": {
        "title": "Statistics & Numbers",
        "examples": [
            "{number} things {authority} didn't teach me about {topic}",
            "I read {number} {content_type} and discovered why they went viral",
            "These are the {number} strategies that give you the highest ROI in {niche}",
            "If you use it right, {platform} is worth more than your degree. Here are {number} ways to {outcome}",
            "{percentage} of people get this wrong about {topic}. Here's the truth..."
        ]
    }
}

// Update the fetchHooks function to use HOOK_CATEGORIES as fallback
export async function fetchHooks() {
    try {
        const response = await fetch('/api/hooks');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching hooks:', error);
        // Fallback to local constant if API fails
        return HOOK_CATEGORIES;
    }
} 