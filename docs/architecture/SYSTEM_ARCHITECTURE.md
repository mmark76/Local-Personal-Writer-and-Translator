# System architecture — planned logical boundaries

The user interacts with a UI; application logic coordinates distinct Writer and Translator capabilities and human review. An owned integration boundary communicates with local Ollama. A separate import/export boundary, if implemented, acts only on user-authorized data and paths. These are responsibilities, not mandated processes, modules or a selected technology.

The application owns source text and output lifecycle; the local provider receives only content required for the explicitly requested operation. Original and generated content remain distinct. Errors must not replace originals or trigger remote inference. Interfaces, error semantics, process/network binding and storage implementation require design and validation after decisions are approved. Domain logic must remain independent of presentation and provider implementation details. Owner for all project boundaries: project owner; implementation assignee pending.
